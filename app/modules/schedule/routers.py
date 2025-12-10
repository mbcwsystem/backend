from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.models import PositionEnum, User
from app.modules.schedule import services
from app.modules.schedule.schemas import ScheduleCreateRequest, ScheduleCreateResponse

router = APIRouter()


def is_supervisor(user: User) -> bool:
    return user.position in{
        PositionEnum.advisor,
        PositionEnum.assistant_manager,
        PositionEnum.manager
    }



def get_schedule_user(user: User = Depends(get_current_user)) :
    if not is_supervisor(user):
         raise HTTPException(403, "바이저 이상만 스케줄 관리 가능합니다.")
    return user


# 스케줄 생성 API
@router.post(
    "/api/schedule/create",
     response_model =  ScheduleCreateResponse,
     status_code=status.HTTP_201_CREATED,
     summary="스케줄 생성"
)
def create_schedule(data : ScheduleCreateRequest,
                    db: Session = Depends(get_db),
                    user = Depends(get_schedule_user)) :
    return services.create_schedule(db, user, data)
