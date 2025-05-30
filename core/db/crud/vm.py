from sqlalchemy.orm import Session
from db.models.vm import VirtualMachine
from db.schemas.vm import VMCreate

def create_vm(db: Session, vm: VMCreate, proxmox_id: int):
    db_vm = VirtualMachine(
        name=vm.name,
        project_id=vm.project_id,
        proxmox_id=proxmox_id
    )
    db.add(db_vm)
    db.commit()
    db.refresh(db_vm)
    return db_vm

def get_vms_by_project(db: Session, project_id: int):
    return db.query(VirtualMachine).filter(VirtualMachine.project_id == project_id).all()
