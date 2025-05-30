import requests
from db.models.user import User

PROXMOX_INT_URL = "http://proxmox:8000"

def create_vm(name: str, user: User):
    data = {
        "name": name,
        "ssh_key": user.ssh_key,
        "node": "pve-devops",
        "template_id": "ubuntu-22.04-standard_22.04-1_amd64.tar.zst",
        "type": "lxc"
    }
    
    res = requests.post(f"{PROXMOX_INT_URL}/api/proxmox/vm/create", json=data, headers={"Content-Type": "application/json"})
    res.raise_for_status()
    return {"proxmox": res.json()}