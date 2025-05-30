import requests
from db.models.user import User

SONAR_URL = "https://sonar.diplom.example"

def create_user(username: str, email: str, full_name: str, password: str):
    data = {
        "login": username,
        "email": email,
        "name": full_name,
        "password": password
    }

    res = requests.post(
        f"{SONAR_URL}/api/v2/users-management/users", 
        json=data, 
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer squ_cb1182fed40d3492633d0eedf515b4f492b74f40"
        }, verify=False)
    res.raise_for_status() 
    return {"sonar": res.json()}
