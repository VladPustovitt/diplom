import httpx

NOTIFY_URL = "http://notify:8000"

async def send_vm_expiry_notification(user_id: int, vm_name: str, expiry_date: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{NOTIFY_URL}/notify/vm_expiry", json={
            "user_id": user_id,
            "vm_name": vm_name,
            "expiry_date": expiry_date
        })
        return response.json()
