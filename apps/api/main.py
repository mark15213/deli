from fastapi import FastAPI

app = FastAPI(title="Gulp API")

@app.get("/")
def read_root():
    return {"message": "Welcome to Gulp API"}
