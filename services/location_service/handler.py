
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
        loc=r['location']
        return db(f"""INSERT INTO ubicacion(codigo,capacidad)
                       VALUES('{loc['codigo']}',{loc['capacidad']})
                       RETURNING id_ubicacion""")
    elif act=='list':
        return db("SELECT * FROM ubicacion")
    else:
        return 'unknown'
Service('location_service', host='esb', port=5001).run_service(handle)
