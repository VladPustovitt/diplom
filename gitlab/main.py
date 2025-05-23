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


ci_config = '''
stages:
    - build
    - test
    - deploy

build:
    stage: build
    image: docker:25.0.4-git
    variables:
        TAG: dev
        DOCKERFILE_PATH: "./Dockerfile"
    before_script:
        - docker login $CI_REGISTRY -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD
    script:
        - DOCKER_BUILDKIT=1 docker build
            --cache-from $CI_REGISTRY/$CI_PROJECT_PATH:latest
            -f $DOCKERFILE_PATH
            --push --rm
            -t $CI_REGISTRY/$CI_PROJECT_PATH:latest
            -t $CI_REGISTRY/$CI_PROJECT_PATH:$TAG .

sast:
    stage: test
    image: sonarsource/sonar-scanner-cli:5.0
    allow_failure: true
    variables:
        SONAR_USER_HOME: "$CI_PROJECT_DIR/.sonar"  # Defines the location of the analysis task cache
        GIT_DEPTH: "0"  # Tells git to fetch all the branches of the project, required by the analysis task
        PROJECT_NAME: $CI_PROJECT_NAME
    before_script:
        - apk add jq
        - SONAR_STATUS=$(curl -k -s -o /dev/null -w "%{http_code}" -u "$SONAR_TOKEN:" -XPOST "${SONAR_HOST_URL}/api/projects/create?mainBranch=${CI_DEFAULT_BRANCH}&name=${CI_PROJECT_PATH_SLUG}&project=${CI_PROJECT_PATH_SLUG}&visibility=private")
        - |
        if [[ $SONAR_STATUS != 200 ]]; then
            SONAR_ERROR=$(curl -k -s -u "$SONAR_TOKEN": -XPOST "${SONAR_HOST_URL}/api/projects/create?mainBranch=${CI_DEFAULT_BRANCH}&name=${CI_PROJECT_PATH_SLUG}&project=${CI_PROJECT_PATH_SLUG}&visibility=private" | jq ".errors[0].msg" -r)
            if [[ $SONAR_ERROR == *"similar key already exists"* ]]; then
            echo "Project already exists, continue scanning"
            else
            echo $SONAR_ERROR
            exit 1
            fi
        fi
        
        - echo "sonar.projectKey=${CI_PROJECT_PATH_SLUG}" > sonar-project.properties
        - echo "sonar.qualitygate.wait=true" >> sonar-project.properties
        # - echo "sonar.exclusions=pnpm-lock.yaml" >> sonar-project.properties
        - echo "sonar.java.binaries=./target/classes" >> sonar-project.properties
        # - echo "sonar.exclusions=src/styles/**" >> sonar-project.properties
    script:
        - sonar-scanner
    cache:
        key: "${CI_JOB_NAME}"
        paths:
        - .sonar/cache

sca:
    stage: test
    allow_failure: true
    script:
        - curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
        - syft . -o cyclonedx-xml=cyclonedx.xml
        - |
        curl -X 'POST' \
        'https://dtrack.hexteam.tech:8080/api/v1/bom' \
        -H 'accept: application/json' \
        -H "X-Api-Key: ${DTRACK_TOKEN}" \
        -H 'Content-Type: multipart/form-data' \
        -F 'autoCreate=true' \
        -F "projectName=$CI_PROJECT_PATH" \
        -F 'projectVersion=1' -F "bom=@cyclonedx.xml" -k --fail

deploy:
    stage: deploy
    variables:
        SSH_KEY: $SSH_KEY_PRIVATE
        DEV_SERVER: $DEV_SERVER
        DEV_USER: root
        PROJECT_DIR: $PROJECT_DIR
        SERVICE_NAME: $SERVICE_NAME
    script:
        - chmod og= $SSH_KEY
        - ssh -i $SSH_KEY -p 22 -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_SERVER} \
            "docker login ${CI_REGISTRY} -u ${CI_REGISTRY_USER} -p ${CI_REGISTRY_PASSWORD} &&
            cd ${PROJECT_DIR} && docker compose pull ${SERVICE_NAME} && docker compose down --remove-orphans &&
            docker compose up -d && docker image prune -f && docker container prune -f"
'''


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
