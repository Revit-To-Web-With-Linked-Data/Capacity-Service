from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"Message": "Frontpage"}

@router.post("/pipes")
async def calculate_pipes():
     return {"Message": "SecondPage"}

