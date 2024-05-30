import sys
import uuid
import time
import pandas as pd
from threading import Thread
from multiprocessing import Process, Manager

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
#UPLOAD_DIR = backend_config["UPLOAD_DIR"]
ORIGINS = backend_config["ALLOWED_ORIGINS"]
STALE_THRESHOLD_DAYS = backend_config["STALE_THRESHOLD_DAYS"]

# 'globals'

manager = Manager()
jobs = manager.dict() # stores progress and results so progress is tracked and can be polled

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
    # generate a unique ID for the job
    job_id = str(uuid.uuid1())

    # default unless uploaded
    yaml_config = Config("configs/defaultLSTM.yaml")

    # time stamp of job creation
    time_stamp = time.time()

    jobs[job_id] = {
        "status": "Initialising",
        "result": None,
        "config": yaml_config,
        "site_name": site_name,
        "time_stamp": time_stamp,
        "activities": [] # stores list of the activity names
    }

    # find any uploaded config file and set for the mine site
    for file in files:
        if file.filename.endswith(".yaml"):
            yaml_config = Config(file.file.read())
    
    target_list = yaml_config["targets"]

    result = {}
    for file in files:
        if file.filename.endswith(".csv"):
            # split to get activity portion from filename:
            # e.g npm_sitename_activity.csv
            activity = file.filename.split('_')[2].split('.')[0]
            
            # workaround of a limitation of a manager dict when dealing with nested dict or lists
            # as modifications of the nested objects are reflected in the shared memory only local
            # requiring the copying of the manager to a non manager equivalent
            temp = jobs[job_id]    
            temp["activities"].append(activity.capitalize())
            jobs[job_id] = temp

            # find target column given an activity
            target_column = target_list[activity]

            # read data frame from file
            data_frame = pd.read_csv(file.file)
            
            # create an activity given the target column and data frame
            new_activity = {"data_frame": data_frame, "target_column": target_column}
            result[activity] = new_activity
    
    temp = jobs[job_id]
    temp["result"] = result
    jobs[job_id] = temp

    # create a sub process to process the job's data
    process = Process(target=process_job,args=[job_id])
    # kill sub process if the main process ends
    process.daemon = True
    process.start()

    return job_id

def process_job(job_id):
    # preprocess the jobs dataframe
    temp = jobs[job_id]
    temp["status"] = "Preprocessing"
    jobs[job_id] = temp

    job = jobs[job_id]
    job = preprocess(job)
    jobs[job_id] = job

    # train and run the models on the preprocessed dataframe
    temp = jobs[job_id]
    temp["status"] = "Running Models"
    jobs[job_id] = temp

    job = jobs[job_id]
    model_runner = ModelRunner()
    job = model_runner.run_model(jobs[job_id])
    jobs[job_id] = job

    # detect drift on the prediction dataframe
    temp = jobs[job_id]
    temp["status"] = "Detecting Drift"
    jobs[job_id] = temp

    drift_detection = DriftDetection()

    job = jobs[job_id]
    for activity in job["result"]:
        df = job["result"][activity]["pred_data_frame"]
        # detected drift on the LSTM column of the dataframe
        target_column = "LSTM"
        date_column = job["config"]["date_column"]
        job["result"][activity]["drift"] = drift_detection.detect_drift(
            df, target_column, date_column
        )
    jobs[job_id] = job

    temp = jobs[job_id]
    temp["status"] = "Complete"
    jobs[job_id] = temp


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
        drift_data = job["result"][activity]["drift"]

        # extract the target column from the data_frame and rename it to "actual"
        actual_data = data_frame[[date_column, target_column]].copy()
        actual_data.rename(columns={target_column: "actual"}, inplace=True)

        # merge the actual data with the pred_data_frame
        merged_data = pd.merge(
            actual_data,
            pred_data_frame,
            on=date_column,
            how="outer",
        )

        # Include the drift data in the result
        # merged_data["drift"] = drift_data["date"]
        results[activity] = {}
        results[activity]["data"] = merged_data.to_json(index=False)
        results[activity]["target_column"] = target_column
        results[activity]["drift"] = drift_data

    return results

###__________________________###
def job_check():
    while True:
        time.sleep(86400)  # sleep for one day
        current_time = time.time()
        stale_time = STALE_THRESHOLD_DAYS * 86400  # convert days to seconds
        stale_jobs = [job_id for job_id, job in jobs.items() if current_time - job["time_stamp"] > stale_time]
        for job_id in stale_jobs:
            del jobs[job_id]


###_______________________###
# start the job check thread
stale_job_thread = Thread(target=job_check)
stale_job_thread.daemon = True
stale_job_thread.start()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=backend_config["HOST"],
        port=backend_config["PORT"],
        reload=backend_config["DEV"],
    )
