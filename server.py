from fastapi import FastAPI
from routes import hydraulics

app = FastAPI()

app.include_router(hydraulics.router)



