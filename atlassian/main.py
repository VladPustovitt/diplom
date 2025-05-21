# main.py
# Requirements:
#   pip install fastapi uvicorn requests

import os
import requests
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import json

# Configuration class
class JiraConfluenceConfig:
    def __init__(self):
        try:
            self.jira_url = os.environ["JIRA_URL"]
            self.jira_user = os.environ["JIRA_USER"]
            self.jira_token = os.environ["JIRA_TOKEN"]
            self.confluence_url = os.environ["CONFLUENCE_URL"]
            self.confluence_user = os.environ["CONFLUENCE_USER"]
            self.confluence_token = os.environ["CONFLUENCE_TOKEN"]
        except KeyError as e:
            raise RuntimeError(f"Missing environment variable: {e.args[0]}")

# Integration client
TEMPLATE_KEY = "com.pyxis.greenhopper.jira:gh-kanban-template"
ALL_CONFLUENCE_PERMISSIONS = [
    {
        "targetType": "space",
        "operationKey": "read"
    },
    {
        "targetType": "space",
        "operationKey": "administer"
    },
    {
        "targetType": "space",
        "operationKey": "export"
    },
    {
        "targetType": "space",
        "operationKey": "restrict"
    },
    {
        "targetType": "space",
        "operationKey": "delete_own"
    },
    {
        "targetType": "space",
        "operationKey": "delete_mail"
    },
    {
        "targetType": "page",
        "operationKey": "create"
    },
    {
        "targetType": "page",
        "operationKey": "delete"
    },
    {
        "targetType": "blogpost",
        "operationKey": "create"
    },
    {
        "targetType": "blogpost",
        "operationKey": "delete"
    },
    {
        "targetType": "comment",
        "operationKey": "create"
    },
    {
        "targetType": "comment",
        "operationKey": "delete"
    },
    {
        "targetType": "attachment",
        "operationKey": "create"
    },
    {
        "targetType": "attachment",
        "operationKey": "delete"
    }
]
class IntegrationClient:
    def __init__(self, config: JiraConfluenceConfig):
        self.config = config
        self.jira_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.jira_token}"
        }
        self.confluence_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.confluence_token}"
        }

    def post(self, base_url, endpoint, data, headers):
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        try:
            return response.json()
        except:
            return response

    def get(self, base_url, endpoint, data, headers):
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.get(url, json=data, headers=headers)
        response.raise_for_status()
        try:
            return response.json()
        except:
            return response

    def put(self, base_url, endpoint, data, headers):
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.put(url, json=data, headers=headers)
        response.raise_for_status()
        try:
            return response.json()
        except:
            return response

    def create_jira_project(self, key: str, name: str, lead: Optional[str], project_type: str):
        data = {
            "key": key,
            "name": name,
            "projectTypeKey": project_type,
            "projectTemplateKey": TEMPLATE_KEY,
            "lead": lead,
        }
        return self.post(self.config.jira_url, "/rest/api/2/project", data, self.jira_headers)

    def create_confluence_space(self, key: str, name: str, description: Optional[str]):
        data1 = {
            "key": key,
            "name": name,
            "description": {
                "plain": {
                    "value": description or "",
                    "representation": "plain"
                }
            }
        }
        return self.post(self.config.confluence_url, "/rest/api/space", data1, self.confluence_headers)

    def create_jira_user(self, username: str, email: str, display_name: str, password: str):
        data = {
            "name": username,
            "password": password,
            "emailAddress": email,
            "displayName": display_name,
            "notification": False
        }
        return self.post(self.config.jira_url, "/rest/api/2/user", data, self.jira_headers)

    def create_confluence_user(self, username: str, email: str, full_name: str, password: str):
        data = {
            "userName": username,
            "email": email,
            "fullName": full_name,
            "password": password,
            "notifyViaEmail": False
        }
        return self.post(self.config.confluence_url, "/rest/api/admin/user", data, self.confluence_headers)

    def assign_all_confluence_space_permissions(self, space_key: str, username: str):
        data = [
            {
                'userKey': username,
                'operations': ALL_CONFLUENCE_PERMISSIONS
            },
            {
                'groupName': "confluence-users",
                'operations': []
            }
        ]
        endpoint = f"/rest/api/space/{space_key}/permissions"
        self.post(self.config.confluence_url, endpoint, data, self.confluence_headers)
        return "all"
    
# Pydantic models
class ProjectCreate(BaseModel):
    key: str = Field(..., min_length=2, max_length=10)
    name: str
    lead: Optional[str]
    project_type: str = Field("software", pattern="^(software|business|service_desk)$")

class BoardCreate(BaseModel):
    name: str
    project_key: str
    board_type: str = Field("scrum", pattern="^(scrum|kanban)$")

class SpaceCreate(BaseModel):
    key: str = Field(..., min_length=2, max_length=10)
    name: str
    description: Optional[str]

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    full_name: str
    password: str = Field(..., min_length=6)

class ConfluencePermissionAssign(BaseModel):
    space_key: str
    username: str

# Initialize app with custom OpenAPI and docs URLs
app = FastAPI(
    title="Jira-Confluence Integration API",
    openapi_url="/api/atlassian/openapi.json",
    docs_url="/api/atlassian/docs",
    redoc_url="/api/atlassian/redoc"
)

# Router for Atlassian API
router = APIRouter(prefix="/api/atlassian")
config = JiraConfluenceConfig()
client = IntegrationClient(config)

@router.post("/projects/")
def create_project(payload: ProjectCreate):
    try:
        project = client.create_jira_project(
            key=payload.key,
            name=payload.name,
            lead=payload.lead,
            project_type=payload.project_type
        )
        return {"status": "success", "project": project}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/spaces/")
def create_space(payload: SpaceCreate):
    try:
        space = client.create_confluence_space(
            key=payload.key,
            name=payload.name,
            description=payload.description
        )
        return {"status": "success", "space": space}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/jira")
def create_jira_user(payload: UserCreate):
    try:
        user = client.create_jira_user(
            username=payload.username,
            email=payload.email,
            display_name=payload.full_name,
            password=payload.password
        )
        return {"status": "success", "user": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/confluence")
def create_confluence_user(payload: UserCreate):
    try:
        user = client.create_confluence_user(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password
        )
        return {"status": "success", "user": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/permissions/confluence")
def assign_all_confluence_permissions(payload: ConfluencePermissionAssign):
    try:
        result = client.assign_all_confluence_space_permissions(
            space_key=payload.space_key,
            username=payload.username
        )
        return {"status": "success", "permissions": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Include router
app.include_router(router)

# Run with: uvicorn main:app --reload