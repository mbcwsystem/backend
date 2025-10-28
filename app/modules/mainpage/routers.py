from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_mainpage():
    return {"message": "Hello World"}
