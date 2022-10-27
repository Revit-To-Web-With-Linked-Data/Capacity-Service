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

@router.post("/pressureDropTees")
async def calculate_pipes(request: Request):
    data = await request.body()
    teeGraph = pressureDrop.tees(json.loads(data))
    return json.dumps(teeGraph)

@router.post("/pressureDropRest")
async def calculate_pipes(request: Request):
    data = await request.body()
    pipeGraph = pressureDrop.pipes(json.loads(data))
    return json.dumps(pipeGraph) 