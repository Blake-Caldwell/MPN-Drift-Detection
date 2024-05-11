import sys
import os

import uuid
import time
import pandas as pd

from fastapi import FastAPI, UploadFile, HTTPException, Query, File
from fastapi.middleware.cors import CORSMiddleware

from src.config.config import Config
from src.input.CSVInputSource import CSVInputSource

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
    #TODO
    # - Only load the versions of the files submitted
    # - Remove the saving of files into uploads
    # - Potentially add more multiprocessing to improve performances
    # - Return the output to the frontend
    
    # Had to add a local definition as the global was not being instantiated
    jobs = {}

    #default config file
    yaml_config = Config("configs/defaultLSTM.yaml")

    # TO BE REDONE
    for file in files:
        data = await file.read()
        save_loc = UPLOAD_DIR + "/" + file.filename
        with open(save_loc, "wb") as saved_f:
            saved_f.write(data)

        #override default config if able
        if file.filename.endswith(".yaml"):
            yaml_config = Config(save_loc)
            #yaml_config["site_name"] = site_name

    site_name_list = yaml_config["site_name"]
    activity_list = yaml_config["activity_list"]
    target_list = yaml_config['targets']

    # TO BE MODIFIED
    for site_name in site_name_list:
        job_id = str(uuid.uuid1())
        result = {}

        time_stamp = time.time()
        jobs[job_id] = {"site_name": site_name, "status": "processing", "config": yaml_config, "time_stamp": time_stamp,"result": None}

        for activity in activity_list:
            data_frame = pd.read_csv(UPLOAD_DIR + f"/mpn_{site_name}_{activity}.csv")
            target_column = target_list[activity]
            new_activity = {"data_frame": data_frame, "target_column": target_column}
            result[activity] = new_activity

        jobs[job_id]['result'] = result

    jobs = preprocess(jobs)
    model_runner = ModelRunner()
    jobs = model_runner.run_model(jobs)

    drift_detection = DriftDetection()

    for key in jobs.keys():
        for activity in jobs[key]['result']:
            df = jobs[key]['result'][activity]['pred_data_frame']
            #target_column = jobs[key]['result'][activity]['target_column']
            target_column = 'LSTM'
            date_column = jobs[key]['config']['date_column']
            jobs[key]['result'][activity]['drift'] = drift_detection.detect_drift(df,target_column,date_column)

    print(jobs)

    #jobs[job_id] = {
    #    "status": "processing",
    #    "result": None,
    #    "config": yaml_config,
    #    "site_name": site_name,
    #}

    # if no config, provide default config
    #if not jobs[job_id]["config"]:
    #    jobs[job_id]["config"] = Config("configs/defaultLSTM.yaml")
    #    jobs[job_id]["config"]["site_name"] = site_name

    # Logic to start processing data gets launched from here
    return job_id


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
