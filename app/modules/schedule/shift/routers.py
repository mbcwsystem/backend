from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_schedule():
    return {"message": "Hello World"}
