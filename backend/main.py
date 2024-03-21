from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def index():
    return {"details": "Hello, World"}


@app.get("/test")
def test():
    return "Hello from FastAPI"
