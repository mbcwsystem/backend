from app.modules.admin import models as admin_models
from app.modules.auth import models as auth_models
from app.modules.community import models as community_models
from app.modules.payroll import models as payroll_models
from app.modules.schedule import models as schedule_models
from app.modules.workstatus import models as workstatus_models

# 필요시 계속 추가

__all__ = [
    "auth_models",
    "admin_models",
    "payroll_models",
    "schedule_models",
    "community_models",
    "workstatus_models",
]
