FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY generate_sample_data.py .
COPY config.py .
COPY models.py .
COPY database.py .
RUN mkdir -p logs
CMD ["python", "generate_sample_data.py"]
