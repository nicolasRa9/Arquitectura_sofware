
import json, socket
from common.services import Service
from common.soa_formatter import soa_formatter
def db(sql:str):
    s = socket.create_connection(('esb',5001))
    s.sendall(soa_formatter('db_manager', sql))
    ln=int(s.recv(5)); data=s.recv(ln)
    return data.decode()[7:]

def handle(data:str)->str:
    r=json.loads(data); act=r.get('action')
    if act=='low_stock':
        thr=r.get('threshold',5)
        return db(f"""SELECT p.nombre, SUM(s.cantidad) total
                       FROM stock s JOIN producto p ON p.id_producto=s.id_producto
                       GROUP BY p.nombre HAVING SUM(s.cantidad)<{thr}""")
    elif act=='efficiency':
        return db("""SELECT DATE(fecha), COUNT(*) FROM movimiento
                      GROUP BY DATE(fecha) ORDER BY DATE(fecha) DESC""")
    return 'unknown'
Service('alert_report_service', host='esb', port=5001).run_service(handle)
