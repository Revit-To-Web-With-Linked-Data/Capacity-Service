from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    await foo()
    return {"Hello": "World"}