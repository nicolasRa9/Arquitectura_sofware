
import json, socket
from common.services import Service
from common.soa_formatter import soa_formatter
def db(sql:str):
    s = socket.create_connection(('esb',5001))
    s.sendall(soa_formatter('db_manager', sql))
    ln=int(s.recv(5)); data=s.recv(ln)
    return data.decode()[7:]

def handle(data:str)->str:
    req=json.loads(data)
    act=req.get('action')
    if act=='create':
        p=req['product']
        sql=f"""INSERT INTO producto(nombre,tamanio,peso,categoria,rotacion)
                 VALUES('{p['nombre']}',{p['tamanio']},{p['peso']},
                        '{p['categoria']}','{p['rotacion']}') RETURNING id_producto"""
        return db(sql)
    elif act=='list':
        return db("SELECT * FROM producto")
    elif act=='get':
        return db(f"SELECT * FROM producto WHERE id_producto={req['id']}")
    elif act=='delete':
        return db(f"DELETE FROM producto WHERE id_producto={req['id']}")
    else:
        return 'unknown action'
Service('product_service', host='esb', port=5001).run_service(handle)
