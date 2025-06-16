
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
    if act=='create':
        items=r['items']
        pid=json.loads(db("INSERT INTO pedido DEFAULT VALUES RETURNING id_pedido"))[0][0]
        for it in items:
            db(f"""INSERT INTO pedido_item(id_pedido,id_producto,cantidad)
                     VALUES({pid},{it['id_producto']},{it['cantidad']})""")
        return json.dumps({"order_id":pid})
    elif act=='status':
        oid=r['order_id']
        return db(f"""SELECT estado FROM pedido WHERE id_pedido={oid}""")
    return 'unknown'
Service('order_service', host='esb', port=5001).run_service(handle)
