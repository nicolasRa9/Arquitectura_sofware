
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
    if act=='map':
        return db("""SELECT u.codigo, p.nombre, s.cantidad
                      FROM stock s
                      JOIN ubicacion u ON u.id_ubicacion=s.id_ubicacion
                      JOIN producto p ON p.id_producto=s.id_producto
                      ORDER BY u.codigo""")
    elif act=='search':
        term=r['term']
        return db(f"""SELECT u.codigo, s.cantidad
                   FROM stock s
                   JOIN ubicacion u ON u.id_ubicacion=s.id_ubicacion
                   JOIN producto p ON p.id_producto=s.id_producto
                   WHERE LOWER(p.nombre) LIKE LOWER('%{term}%')""")
    return 'unknown'
Service('visualization_service', host='esb', port=5001).run_service(handle)
