import os

class Settings:
    postgres_user: str = os.environ["POSTGRES_USER"]
    postgres_password: str = os.environ["POSTGRES_PASSWORD"]
    postgres_db: str = os.environ["POSTGRES_DB"]
    postgres_host: str = os.environ["POSTGRES_HOST"]
    postgres_port: int = os.environ["POSTGRES_PORT"]

    gitlab_int_url: str = os.environ["GITLAB_INT_URL"]
    proxmox_int_url: str = os.environ["PROXMOX_INT_URL"]
    atlassian_int_url: str = os.environ["ATLASSIAN_INT_URL"]
    notify_url: str = os.environ["NOTIFY_URL"]

settings = Settings()
