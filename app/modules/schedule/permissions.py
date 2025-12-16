from app.modules.auth.models import PositionEnum, User


def is_supervisor(user: User) -> bool:
    return user.position in {
        PositionEnum.advisor,
        PositionEnum.assistant_manager,
        PositionEnum.manager,
    }
