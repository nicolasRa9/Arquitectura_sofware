FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir psycopg2-binary
COPY common /app/common
COPY services/location_service/handler.py /app/handler.py
CMD ["python","/app/handler.py"]