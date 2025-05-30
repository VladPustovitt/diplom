import requests
from db.models.user import User

DTRACK_URL = "http://dtrack.diplom.example"

def create_user(username: str, email: str, full_name: str, password: str):
    data = {
        "username": username,
        "email": email,
        "name": full_name,
        "newPassword": password,
        "newPassword": password,
        "lastPasswordChange": "2019-08-24T14:15:22Z"
    }

    res = requests.put(
        f"{DTRACK_URL}/api/v1/user/managed", 
        json=data, 
        headers={
            "Content-Type": "application/json", 
            "X-API-Key": "odt_ZLMGBfg9_jzOsr2SahEVv0XorqB4zGBbsC8DRvBkk"
        }, verify=False)
    res.raise_for_status() 
    return {"dtrack": res.json()}