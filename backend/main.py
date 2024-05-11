import sys
import os

import uuid

from fastapi import FastAPI, UploadFile, HTTPException, Query, File
from fastapi.middleware.cors import CORSMiddleware

from src.config.config import Config

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

    print(f"{job_id} | {site_name}")

    yaml_config = None

    # these shouldn't be stored but instead forwarded to the models
    for file in files:
        data = await file.read()
        save_loc = UPLOAD_DIR + "/" + file.filename
        with open(save_loc, "wb") as saved_f:
            saved_f.write(data)

        if file.filename.endswith(".yaml"):
            yaml_config = Config(save_loc)
            yaml_config["site_name"] = site_name

    jobs[job_id] = {
        "status": "processing",
        "result": None,
        "config": yaml_config,
        "site_name": site_name,
        "progress": 0,  # to be used as 0-100 for progress bar
    }

    # if no config, provide default config
    if not jobs[job_id]["config"]:
        jobs[job_id]["config"] = Config("configs/defaultLSTM.yaml")
        jobs[job_id]["config"]["site_name"] = site_name

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
