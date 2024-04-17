from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# 'consts'
UPLOAD_DIR = "uploads"

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"details": "Hello, World"}


@app.get("/test")
def test():
    return "Hello from FastAPI"


# file uploading
# this in the future should be session driven. i.e files are stored to a session id. future problem however
@app.post("/upload_files")
async def upload_files(files: list[UploadFile]):
    for file in files:
        data = await file.read()
