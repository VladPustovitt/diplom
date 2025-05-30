import requests
from db.models.user import User

ATLASSIAN_INT_URL = "http://atlassian:8000"

def create_jira_confluence_user(username: str, email: str, full_name: str, password: str):
    data = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "password": password
    }
    res1 = requests.post(f"{ATLASSIAN_INT_URL}/api/atlassian/users/jira", json=data, headers={"Content-Type": "application/json"})
    res1.raise_for_status()
    res2 = requests.post(f"{ATLASSIAN_INT_URL}/api/atlassian/users/confluence", json=data, headers={"Content-Type": "application/json"})
    res2.raise_for_status()
    return {"jira": res1.json(), "confluence": res2.json()}


def create_jira_confluence(project_name: str, user: User):
    data_jira = {
        "key": project_name[:3].upper(),
        "name": project_name,
        "lead": user.username,
        "project_type": "software"
    }
    data_conflience = {
        "key": project_name[:3].upper(),
        "name": project_name,
        "description": f"This space for {project_name}"
    }

    res1 = requests.post(f"{ATLASSIAN_INT_URL}/api/atlassian/projects", json=data_jira, headers={"Content-Type": "application/json"})
    res1.raise_for_status()
    res2 = requests.post(f"{ATLASSIAN_INT_URL}/api/atlassian/spaces", json=data_conflience, headers={"Content-Type": "application/json"})
    res2.raise_for_status()
    res3 = requests.post(f"{ATLASSIAN_INT_URL}/api/atlassian/", json={"space_key": res2["spaceKey"], "username": user.username}, headers={"Content-Type": "application/json"})
    res3.raise_for_status()
    return {"jira": res1.json(), "confluence": res2.json()}
