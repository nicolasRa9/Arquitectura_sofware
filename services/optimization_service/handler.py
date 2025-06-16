
import json, socket
from common.services import Service
from common.soa_formatter import soa_formatter
def db(sql:str):
    s = socket.create_connection(('esb',5001))
    s.sendall(soa_formatter('db_manager', sql))
    ln=int(s.recv(5)); data=s.recv(ln)
    return data.decode()[7:]

def handle(data:str)->str:
    r=json.loads(data)
    if r.get('action')=='suggest':
        pid=r['product_id']; qty=r['qty']
        rows = json.loads(db("""SELECT id_ubicacion,capacidad,
                                      COALESCE((SELECT SUM(cantidad*p.tamanio)
                                                FROM stock s
                                                JOIN producto p ON p.id_producto=s.id_producto
                                                WHERE s.id_ubicacion=u.id_ubicacion),0) AS usado
                             FROM ubicacion u"""))
        best=None; bestfree=-1
        for uid,cap,used in rows:
            free=cap-float(used)
            if free>=qty and free>bestfree:
                bestfree=free; best=uid
        return json.dumps({"suggested_location":best})
    return 'unknown'
Service('optimization_service', host='esb', port=5001).run_service(handle)
