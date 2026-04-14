from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
def report_ping():
    return {"message": "report placeholder"}