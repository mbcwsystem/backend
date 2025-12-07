from app.modules.auth.models import PositionEnum

ADMIN_ROLES = {
    PositionEnum.manager,
    PositionEnum.assistant_manager,
    PositionEnum.advisor,
}

STAFF_ROLES = {
    PositionEnum.leader,
    PositionEnum.crew,
    PositionEnum.cleaner,
}

SYSTEM_ROLES = PositionEnum.system


# 관리자 여부
def is_admin(user) -> bool:  # 관리자
    return user.position in ADMIN_ROLES


def is_staff(user) -> bool:  # 일반
    return user.position in STAFF_ROLES


def is_system(user) -> bool:  # 시스템
    return user.position == SYSTEM_ROLES
