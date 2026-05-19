FROM python:3.12.7 
WORKDIR /app
COPY . . 
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app
CMD ["python", "main.py"]