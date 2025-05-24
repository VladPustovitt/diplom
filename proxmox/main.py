from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from proxmox_client import create_qemu_vm, create_lxc_container, wait_for_lxc_ready, wait_for_ssh
from vm_configurator import configure_vm

router = APIRouter(prefix="/api/proxmox", tags=["Proxmox VE Integration"])

class VMCreateRequest(BaseModel):
    name: str
    node: str = "pve-devops"
    template_id: str = "ubuntu-22.04-standard_22.04-1_amd64.tar.zst"
    ssh_key: str
    type: str = "lxc"  # qemu или lxc

@router.post("/vm/create")
async def create_virtual_machine(req: VMCreateRequest):
    try:
        if req.type == "qemu":
            vm_id = create_qemu_vm(req.name, req.node, req.template_id)
        elif req.type == "lxc":
            vm_id = create_lxc_container(req.name, req.node, req.template_id)
            wait_for_lxc_ready(req.node, vm_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid type: must be 'qemu' or 'lxc'")
        wait_for_ssh(f"192.168.100.{vm_id}")
        configure_vm(vm_id, req.ssh_key)
        return {"status": "success", "vm_id": vm_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
app = FastAPI(
    title="Proxmox VE Integration API",
    openapi_url="/api/proxmox/openapi.json",
    docs_url="/api/proxmox/docs",
    redoc_url="/api/proxmox/redoc"
)

app.include_router(router)