from auth.auth_routers import router_auth
from tasks.routers import router_task
from config.db_config import app

app.include_router(router_auth)
app.include_router(router_task)

