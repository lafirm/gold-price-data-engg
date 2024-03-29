FROM apache/airflow:2.6.0-python3.10
COPY requirements.txt .
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r requirements.txt