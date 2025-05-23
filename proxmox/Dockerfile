FROM python:3.13.3-bookworm
ENV ANSIBLE_HOST_KEY_CHECKING False

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]