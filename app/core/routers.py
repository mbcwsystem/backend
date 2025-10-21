from fastapi import APIRouter

api_router = APIRouter()

routers = [
    ("/auth",      "Auth",       "app.modules.auth.routers"),
    ("/schedule",  "Schedule",   "app.modules.schedule.routers"),
    ("/shift",     "Shift",      "app.modules.shift.routers"),
    ("/dayoff",    "DayOff",     "app.modules.dayoff.routers"),
    ("/payroll",   "Payroll",    "app.modules.payroll.routers"),
    ("/community", "Community",  "app.modules.community.routers"),
    ("/mainpage",  "MainPage",   "app.modules.mainpage.routers"),
    ("/admin",     "Admin",      "app.modules.admin.routers"),
]

for prefix, tag, module_path in routers:
    module = __import__(module_path, fromlist=["router"])
    api_router.include_router(module.router, prefix=prefix, tags=[tag])