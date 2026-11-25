from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from store import list_sources, get_chunks

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/api/files")
def files():
    return {"files": list_sources()}


@app.get("/api/files/{name}/chunks")
def file_chunks(name: str):
    chunks = get_chunks(name)
    if not chunks:
        raise HTTPException(status_code=404, detail="No such document")
    return {"file": name, "chunks": chunks}