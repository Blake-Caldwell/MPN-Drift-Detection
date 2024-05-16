import sys
import os

import uuid
import time
import pandas as pd
from threading import Thread

from fastapi import FastAPI, UploadFile, HTTPException, Query, File
from fastapi.middleware.cors import CORSMiddleware

from src.config.config import Config
from src.processing.ModelRunner import ModelRunner
from src.preprocessing.DataProcessor import preprocess
from src.drift.DriftDetection import DriftDetection

if len(sys.argv) > 1:
    config_file = sys.argv[1]
else:
    config_file = "configs/default.yaml"  # this makes having this essential. Maybe we dont want this but I think it's fine

backend_config = Config(config_file)

# 'consts'
UPLOAD_DIR = backend_config["UPLOAD_DIR"]
ORIGINS = backend_config["ALLOWED_ORIGINS"]

# 'globals'

jobs = {}  # stores progress and results so progress is tracked and can be polled

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    return {"details": "--Drift Detector Backend--"}


@app.get("/health")  # required for github action docker build
async def health_check():
    return {"status": "OK"}


@app.get("/test")
def test():
    return "Hello from FastAPI"


# also a config file should be used to only allow certain file types
@app.post("/upload_files")
async def upload_files(
    site_name: str = Query(...), files: list[UploadFile] = File(...)
):

    job_id = str(uuid.uuid1())

    # print(f"{job_id} | {site_name}")

    # default unless uploaded
    yaml_config = Config("configs/defaultLSTM.yaml")

    # Should be redone to not save files
    for file in files:
        data = await file.read()
        save_loc = UPLOAD_DIR + "/" + file.filename
        with open(save_loc, "wb") as saved_f:
            saved_f.write(data)

        if file.filename.endswith(".yaml"):
            yaml_config = Config(save_loc)
            yaml_config["site_name"] = site_name

    time_stamp = time.time()

    jobs[job_id] = {
        "status": "processing",
        "result": None,
        "config": yaml_config,
        "site_name": site_name,
        "time_stamp": time_stamp,
        "progress": 0,  # to be used as 0-100 for progress bar
    }

    activity_list = yaml_config["activity_list"]
    target_list = yaml_config["targets"]

    result = {}
    for activity in activity_list:
        data_frame = pd.read_csv(
            UPLOAD_DIR + "/" + "mpn_" + site_name + "_" + activity + ".csv"
        )
        target_column = target_list[activity]
        new_activity = {"data_frame": data_frame, "target_column": target_column}
        result[activity] = new_activity

    jobs[job_id]["result"] = result

    thread = Thread(target=process_job, args=[job_id])
    # if main thread is closed kill and sub threads
    thread.daemon = True
    thread.start()

    return job_id


def process_job(job_id):
    jobs[job_id]["status"] = "Preprocessing"
    preprocess(jobs[job_id])

    jobs[job_id]["status"] = "Running models"
    model_runner = ModelRunner()
    model_runner.run_model(jobs[job_id])
    jobs[job_id]["progress"] = 10

    jobs[job_id]["status"] = "Detecting Drift"
    drift_detection = DriftDetection()
    for activity in jobs[job_id]["result"]:
        df = jobs[job_id]["result"][activity]["pred_data_frame"]
        target_column = "LSTM"
        date_column = jobs[job_id]["config"]["date_column"]
        jobs[job_id]["result"][activity]["drift"] = drift_detection.detect_drift(
            df, target_column, date_column
        )

    jobs[job_id]["status"] = "Complete"
    jobs[job_id]["progress"] = 100

    # print(jobs[job_id])


@app.get(
    "/job/{job_id}"
)  # stopped the duplicating of the fetch functions, now query at one point
async def get_job(job_id: str, fields: str = None):

    if job_id not in jobs:
        raise HTTPException(404, detail=f"Job id: {job_id} not found")

    job = jobs[job_id]

    if fields:
        requested_fields = fields.split(",")
        job = {field: job[field] for field in requested_fields if field in job}

    return job


@app.get("/job/{job_id}/results")
async def get_job_results(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, detail=f"Job id: {job_id} not found")

    job = jobs[job_id]

    if job["status"] != "Complete":
        raise HTTPException(400, detail=f"Job {job_id} is not completed yet")

    results = {}
    for activity in job["result"]:
        data_frame = pd.DataFrame(job["result"][activity]["data_frame"])
        pred_data_frame = pd.DataFrame(job["result"][activity]["pred_data_frame"])
        target_column = job["result"][activity]["target_column"]
        date_column = "DATE"  # Assuming the date column is always "DATE"
        # drift_data = job["result"][activity]["drift"]

        # extract the target column from the data_frame and rename it to "actual"
        actual_data = data_frame[[date_column, target_column]].copy()
        actual_data.rename(columns={target_column: "actual"}, inplace=True)

        # merge the actual data with the pred_data_frame
        merged_data = pd.merge(
            actual_data,
            pred_data_frame,
            on=date_column,
            how="left",
        )

        # print(job["result"][activity]["pred_data_frame"])
        # print(actual_data)

        # Include the drift data in the result
        # merged_data["drift"] = drift_data["date"]

        results[activity] = merged_data.to_json(index=False)

    # print(results)

    return results


if __name__ == "__main__":
    import uvicorn

    # create upload dir if doesn't exist yet
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    uvicorn.run(
        "main:app",
        host=backend_config["HOST"],
        port=backend_config["PORT"],
        reload=backend_config["DEV"],
    )
