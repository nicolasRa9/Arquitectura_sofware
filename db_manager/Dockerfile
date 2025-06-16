FROM python:3.12-slim
WORKDIR /app
RUN pip install psycopg2-binary
COPY common /app/common
COPY db_manager/db_manager.py /app/db_manager.py
CMD ["python","/app/db_manager.py"]