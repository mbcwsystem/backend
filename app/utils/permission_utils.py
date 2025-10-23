from app.core.config import ADMIN_ROLES

# 관리자 여부
class RoleChecker:
    @staticmethod
    def is_admin(position: str) -> bool: # 관리자
        return position in ADMIN_ROLES

    @staticmethod
    def is_staff(position: str) -> bool: # 일반
        return position not in ADMIN_ROLES