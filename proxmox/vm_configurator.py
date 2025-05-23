import os

def configure_vm(vm_id: int, ssh_key: str):
    cmd = f''' bash /app/ansible/script.sh {vm_id} "{ssh_key}" '''
    print(os.popen(cmd).read())
    