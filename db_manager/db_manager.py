import os, psycopg2, json
from common.services import Service
def exec_sql(sql:str):
    conn=psycopg2.connect(
        host=os.getenv("DB_HOST","db"),
        user=os.getenv("DB_USER","postgres"),
        password=os.getenv("DB_PASSWORD","postgres"),
        dbname=os.getenv("DB_NAME","wms"))
    with conn, conn.cursor() as cur:
        cur.execute(sql)
        if cur.description:
            return json.dumps(cur.fetchall(), default=str)
        return "ok"
Service("db_manager", host="esb", port=5001).run_service(exec_sql)