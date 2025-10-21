from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_payroll():
    return {"message": "Hello World"}