from urllib.request import Request
from fastapi import APIRouter, Request
import json
from fastapi.responses import JSONResponse
import os
from services import pressureDrop
router = APIRouter()
import json

@router.get("/")
async def root():
    return {"Message": "Frontpage"}

@router.post("/tees")
async def calculate_pipes(request: Request):
    sb =""
    data = await request.body()
    pipeGraph = pressureDrop.tees(json.loads(data))
    #sb = json.dumps(data)
    #sb = request.body()
    #return {await request.body()}
    return json.dumps(pipeGraph)

@router.post("/pipes")
async def calculate_pipes(request: Request):
    sb =""
    data = await request.body()
    pipeGraph = pressureDrop.pipes(json.loads(data))
    #sb = json.dumps(data)
    #sb = request.body()
    #return {await request.body()}
    return json.dumps(pipeGraph)