import ansible_runner

def configure_vm(vm_id: int, ssh_key: str):
    with open("/app/ansible/inventory", "w") as file:
        file.write(f"192.168.100.{vm_id}")
    
    extra_vars = {
        "ssh_user": "root",
        "ssh_key": ssh_key
    }
    result = ansible_runner.run(
        playbook='/app/ansible/init_vm.yml',  # Путь к плейбуку
        inventory='/app/ansible/inventory',         # Путь к inventory-файлу
        extravars=extra_vars
    )
    
    return result.status
