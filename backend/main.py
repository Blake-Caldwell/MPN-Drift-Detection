import sys
import os

import uuid

from fastapi import FastAPI, UploadFile, HTTPException
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
async def upload_files(files: list[UploadFile]):

    job_id = str(uuid.uuid1())

    yaml_config = None

    # these shouldn't be stored but instead forwarded to the models
    for file in files:
        data = await file.read()
        save_loc = UPLOAD_DIR + "/" + file.filename
        with open(save_loc, "wb") as saved_f:
            saved_f.write(data)

        if file.filename.endswith(".yaml"):
            yaml_config = Config(save_loc)

    jobs[job_id] = {"status": "processing", "result": None, "config": yaml_config}

    # if no config, provide default config
    if not jobs[job_id]["config"]:
        jobs[job_id]["config"] = Config("configs/defaultLSTM.yaml")

    # Logic to start processing data gets launched from here
    return {"job_id": job_id}


@app.get("/progress/{job_id}")
async def progress(job_id):

    if job_id not in jobs:
        raise HTTPException(404, detail="Job id: " + job_id + "not found")

    return jobs[job_id]


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
