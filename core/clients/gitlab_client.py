import requests
from db.models.user import User

GITLAB_INT_URL = "http://gitlab:8000"

def create_user(username: str, email: str, full_name: str, password: str):
    data = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "password": password
    }

    res = requests.post(f"{GITLAB_INT_URL}/api/gitlab/user", json=data, headers={"Content-Type": "application/json"})
    res.raise_for_status() 
    return {"gitlab": res.json()}

def create_project(name: str, path: str, user: User):
    data1 = {
        "name": name,
        "path": path 
    }
    res1 = requests.post(f"{GITLAB_INT_URL}/api/gitlab/group", json=data1, headers={"Content-Type": "application/json"})
    res1.raise_for_status() 

    data2 = {
        "user_id": user.gitlab_id,
        "group_id": res1.json()["id"],
        "access_level": 50
    }
    res2 = requests.post(f"{GITLAB_INT_URL}/api/gitlab/group/member", json=data2, headers={"Content-Type": "application/json"})
    res2.raise_for_status()
    data3 = {
        "name": "ci-config",
        "namespace_id": res1.json()["id"],
        "initialize_with_readme": False
    }
    res3 = requests.post(f"{GITLAB_INT_URL}/api/gitlab/project", json=data3, headers={"Content-Type": "application/json"})
    print(res3.text)
    res3.raise_for_status()

    config = requests.get(f"{GITLAB_INT_URL}/api/gitlab/default/ci/config").json()["config"]
    print(config)

    data4 = {
        "project_id": res3.json()["id"],
        "content": config
    }
    res4 = requests.post(f"{GITLAB_INT_URL}/api/gitlab/project/ci", json=data4, headers={"Content-Type": "application/json"})
    res4.raise_for_status()

    return {"group": res1.json(), "project": res3.json()}
