from fastapi import APIRouter

from app.modules.wage.routers import admin_router

api_router = APIRouter()

routers = [
    ("/auth", "Auth", "app.modules.auth.routers"),
    ("/schedule", "Schedule", "app.modules.schedule.routers"),
    ("/shift", "Shift", "app.modules.shift.routers"),
    ("/dayoff", "DayOff", "app.modules.dayoff.routers"),
    ("/payroll", "Payroll", "app.modules.payroll.routers"),
    ("/attendance", "Attendance", "app.modules.attendance.routers"),
    ("/community", "Community", "app.modules.community.routers"),
    ("/mainpage", "MainPage", "app.modules.mainpage.routers"),
    ("/admin", "Admin", "app.modules.admin.routers"),
    ("/wage", "Wage", "app.modules.wage.routers"),
]

for prefix, tag, module_path in routers:
    module = __import__(module_path, fromlist=["router"])
    api_router.include_router(module.router, prefix=prefix, tags=[tag])

api_router.include_router(admin_router, prefix="/admin/default-wage", tags=["Admin"])
