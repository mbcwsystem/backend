from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_dayoff():
    return {"message": "Hello World"}
