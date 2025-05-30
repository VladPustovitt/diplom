from fastapi import FastAPI
from api.routes import users, projects, vms
from db.session import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from web_routes import router as web_router
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from web_routes import templates
from fastapi.staticfiles import StaticFiles

# Инициализация БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Core Service for Secure DevOps",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS (настрой по необходимости)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(vms.router, prefix="/api/vms", tags=["Virtual Machines"])
app.include_router(web_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "Core module is running"}

@app.exception_handler(404)
def not_found(request: Request, exc):
    return templates.TemplateResponse("error.html", {"request": request, "message": "Страница не найдена"}, status_code=404)

@app.exception_handler(403)
def forbidden(request: Request, exc):
    return templates.TemplateResponse("error.html", {"request": request, "message": "Доступ запрещён"}, status_code=403)


