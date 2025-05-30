from sqlalchemy.orm import Session
from db.crud.vm import create_vm, get_vms_by_project
from db.schemas.vm import VMCreate
from clients.proxmox_client import create_vm as create_proxmox
from db.models.user import User

def create_project_vm(db: Session, vm: VMCreate, user: User):
    proxmox = create_proxmox(vm.project_name, user.ssh_key)
    return create_vm(db, vm, proxmox["proxmox"]["proxmox"]["vm_id"])

def list_project_vms(db: Session, project_id: int):
    return get_vms_by_project(db, project_id)
