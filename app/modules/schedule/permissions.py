from app.modules.auth.models import User, PositionEnum


def is_supervisor(user: User) -> bool:
    return user.position in {
        PositionEnum.advisor,
        PositionEnum.assistant_manager,
        PositionEnum.manager,
    }