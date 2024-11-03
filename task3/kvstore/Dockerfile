FROM python:3.9

WORKDIR /workspace

COPY requirements.txt /workspace/
RUN pip install -r requirements.txt

COPY . /workspace/

WORKDIR /workspace/kv_store

EXPOSE 8000 8001

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

