from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import requests
import os

# Настройки GitLab
GITLAB_URL = os.getenv("GITLAB_URL")
GITLAB_API = f"{GITLAB_URL}/api/v4"
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")

headers = {
    "PRIVATE-TOKEN": GITLAB_TOKEN,
    "Content-Type": "application/json"
}

router = APIRouter(prefix="/api/gitlab", tags=["GitLab Integration"])

# Модели данных
class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    full_name: str

class GroupCreateRequest(BaseModel):
    name: str
    path: str

class GroupMembershipRequest(BaseModel):
    user_id: int
    group_id: int
    access_level: int = 40  # Maintainer

class ProjectCreateRequest(BaseModel):
    name: str
    namespace_id: int
    initialize_with_readme: bool = True

class CICDTemplateRequest(BaseModel):
    project_id: int
    content: str

# 1. Создание пользователя
@router.post("/user")
def create_user(data: UserCreateRequest):
    r = requests.post(f"{GITLAB_API}/users", headers=headers, json={
        "email": data.email,
        "password": data.password,
        "username": data.username,
        "name": data.full_name,
        "skip_confirmation": True
    }, verify=False)
    if r.status_code not in [201, 409]:
        raise HTTPException(status_code=400, detail=r.json())
    if r.status_code == 201:
        return r.json()
    else:
        users = requests.get(f"{GITLAB_API}/users?username={data.username}", headers=headers, verify=False)
        return users.json()[0]

# 2. Создание группы
@router.post("/group")
def create_group(data: GroupCreateRequest):
    r = requests.post(f"{GITLAB_API}/groups", headers=headers, json=data.dict(), verify=False)
    if r.status_code not in [201, 409]:
        raise HTTPException(status_code=400, detail=r.json())
    if r.status_code == 201:
        return r.json()
    else:
        groups = requests.get(f"{GITLAB_API}/groups?search={data.path}", headers=headers, verify=False)
        return groups.json()[0]

# 3. Добавление пользователя в группу
@router.post("/group/member")
def add_user_to_group(data: GroupMembershipRequest):
    r = requests.post(f"{GITLAB_API}/groups/{data.group_id}/members", headers=headers, json={
        "user_id": data.user_id,
        "access_level": data.access_level
    }, verify=False)
    if r.status_code not in [201, 409]:
        raise HTTPException(status_code=400, detail=r.json())
    return {"status": "added", "code": r.status_code}

# 4. Создание проекта
@router.post("/project")
def create_project(data: ProjectCreateRequest):
    r = requests.post(f"{GITLAB_API}/projects", headers=headers, json=data.dict(), verify=False)
    if r.status_code != 201:
        raise HTTPException(status_code=400, detail=r.json())
    return r.json()

# 5. Добавление .gitlab-ci.yml
@router.post("/project/ci")
def add_ci_config(data: CICDTemplateRequest):
    r = requests.get(f"{GITLAB_API}/projects/{data.project_id}", headers=headers, verify=False)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get project")
    default_branch = r.json()["default_branch"]

    r = requests.post(f"{GITLAB_API}/projects/{data.project_id}/repository/files/.gitlab-ci.yml", headers=headers, json={
        "branch": default_branch,
        "content": data.content,
        "commit_message": "Add CI/CD config"
    }, verify=False)
    if r.status_code not in [201, 400]:
        raise HTTPException(status_code=400, detail="Failed to add CI/CD config")
    return {"status": "ci config added", "code": r.status_code}

# Создание приложения с доступом к Swagger на /api/gitlab/docs
app = FastAPI(
    title="Gitlab Integration API",
    openapi_url="/api/gitlab/openapi.json",
    docs_url="/api/gitlab/docs",
    redoc_url="/api/gitlab/redoc"
)
app.include_router(router)
