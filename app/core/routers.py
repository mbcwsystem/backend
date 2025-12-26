from fastapi import APIRouter

from app.modules.wage.routers import admin_router

api_router = APIRouter()

routers = [
    ("/auth", "Auth", "app.modules.auth.routers"),
    ("/schedule", "Schedule", "app.modules.schedule.routers"),
    ("/shift", "Shift", "app.modules.shift.routers"),
    ("/dayoff", "DayOff", "app.modules.dayoff.routers"),
    ("/payroll", "급여관리", "app.modules.payroll.router.routers"),
    ("/workstatus", "근태관리", "app.modules.workstatus.routers"),
    ("/community", "Community", "app.modules.community.routers"),
    ("/admin", "Admin", "app.modules.admin.routers"),
    ("/wage", "Wage", "app.modules.wage.routers"),
]

for prefix, tag, module_path in routers:
    module = __import__(module_path, fromlist=["router"])
    api_router.include_router(module.router, prefix=prefix, tags=[tag])

api_router.include_router(admin_router, prefix="/admin/default-wage", tags=["Admin"])
