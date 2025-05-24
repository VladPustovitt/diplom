import os

PROXMOX_HOST = os.environ["PVE_HOST"]
PROXMOX_USER = os.environ["PVE_USER"]
PROXMOX_TOKEN_NAME = os.environ["PVE_API_TOKEN_ID"]
PROXMOX_TOKEN = os.environ["PVE_API_TOKEN"]

with open("/root/.ssh/id_ed25519.pub", "r") as file:
    SSH_KEY = file.read()
