
import json, socket
from common.services import Service
from common.soa_formatter import soa_formatter
def db(sql:str):
    s = socket.create_connection(('esb',5001))
    s.sendall(soa_formatter('db_manager', sql))
    ln=int(s.recv(5)); data=s.recv(ln)
    return data.decode()[7:]

def adjust(pid, loc, delta):
    db(f"""INSERT INTO stock(id_producto,id_ubicacion,cantidad)
             VALUES({pid},{loc},{delta})
             ON CONFLICT(id_producto,id_ubicacion)
             DO UPDATE SET cantidad=stock.cantidad+({delta})""")
def handle(data:str)->str:
    r=json.loads(data)
    if r.get('action')=='move':
        pid=r['product_id']; src=r['from']; dst=r['to']; qty=r['qty']
        adjust(pid, src, -qty)
        adjust(pid, dst, qty)
        db(f"""INSERT INTO movimiento(id_producto,origen,destino,cantidad)
                 VALUES({pid},{src},{dst},{qty})""")
        return 'moved'
    return 'unknown'
Service('movement_service', host='esb', port=5001).run_service(handle)
