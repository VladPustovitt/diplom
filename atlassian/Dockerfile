FROM python:3.13.3-slim-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY main.py .

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["python", "main.py"]