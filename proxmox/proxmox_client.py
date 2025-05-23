import requests
import socket
from config import PROXMOX_HOST, PROXMOX_USER, PROXMOX_TOKEN_NAME, PROXMOX_TOKEN
import time

BASE_URL = f"https://{PROXMOX_HOST}:8006/api2/json"
HEADERS = {
    "Authorization": f"PVEAPIToken={PROXMOX_USER}!{PROXMOX_TOKEN_NAME}={PROXMOX_TOKEN}"
}

# Получение следующего доступного ID для VM/LXC
def get_next_id() -> int:
    url = f"{BASE_URL}/cluster/nextid"
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    return int(response.json()["data"])

# Создание виртуальной машины на основе шаблона
def create_qemu_vm(name: str, node: str, template_id: int) -> int:
    vm_id = get_next_id()
    clone_url = f"{BASE_URL}/nodes/{node}/qemu/{template_id}/clone"
    payload = {
        "newid": vm_id,
        "name": name,
        "full": 1
    }
    response = requests.post(clone_url, headers=HEADERS, data=payload, verify=False)
    response.raise_for_status()
    return vm_id

# Создание LXC контейнера на основе шаблона
def create_lxc_container(name: str, node: str, template_id: str="ubuntu-22.04-standard_22.04-1_amd64.tar.zst") -> int:
    vm_id = get_next_id()
    url = f"{BASE_URL}/nodes/{node}/lxc"
    payload = {
        "vmid": vm_id,
        "hostname": name,
        "ostemplate": f"local:vztmpl/{template_id}",
        "memory": 1024,
        "cores": 1,
        "net0": f"name=eth0,bridge=vmbr1,ip=192.168.100.{vm_id}/24,gw=192.168.100.1",
        "rootfs": "local-lvm:8",  # 8GB
        "ssh-public-keys": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBnJAmNn3jrNaBuvpNrA06S3ijw35EhHbnRraeHNaMSc vspustovit@DESKTOP-BKBT4QJ",
        "unprivileged": 1,
        "nameserver": "8.8.8.8",
        "start": 1,
        "cmode": "shell"
    }
    response = requests.post(url, headers=HEADERS, data=payload, verify=False)
    print(response.json())
    response.raise_for_status()
    return vm_id

def wait_for_lxc_ready(node: str, vm_id: int, timeout: int = 60):
    url = f"{BASE_URL}/nodes/{node}/lxc/{vm_id}/status/current"
    start_time = time.time()

    while True:
        response = requests.get(url, headers=HEADERS, verify=False)
        if response.status_code == 200:
            status = response.json().get("data", {}).get("status", "")
            if status == "running":
                print(f"LXC {vm_id} is up and running.")
                return
        if time.time() - start_time > timeout:
            raise TimeoutError(f"LXC {vm_id} did not start within {timeout} seconds.")
        time.sleep(3)

def wait_for_ssh(ip: str, port: int = 22, timeout: int = 60):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((ip, port), timeout=3):
                print(f"SSH доступен на {ip}:{port}")
                return
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass

        if time.time() - start_time > timeout:
            raise TimeoutError(f"SSH не стал доступен на {ip}:{port} за {timeout} секунд")
        time.sleep(2)
