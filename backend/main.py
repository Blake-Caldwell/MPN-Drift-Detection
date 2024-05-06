import sys
import os

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.config import Config

if len(sys.argv) > 1:
    config_file = sys.argv[1]
else:
    config_file = "configs/default.yaml"  # this makes having this essential. Maybe we dont want this but I think it's fine

backend_config = Config(config_file)

# 'consts'
UPLOAD_DIR = backend_config["UPLOAD_DIR"]
ORIGINS = backend_config["ALLOWED_ORIGINS"]

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


# file uploading
# this in the future should be session driven. i.e files are stored to a session id.
# also a config file should be used to only allow certain file types
@app.post("/upload_files")
async def upload_files(files: list[UploadFile]):
    for file in files:
        data = await file.read()
        save_loc = UPLOAD_DIR + "/" + file.filename
        with open(save_loc, "wb") as saved_f:
            saved_f.write(data)

        if file.filename.endswith('.yaml'):
            yaml_config = Config(save_loc)


    # Logic to start processing data gets launched from here?
    return {"filenames": [saved_f for f in files], "config": yaml_config}

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
