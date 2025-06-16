import argparse, json, socket, sys, pathlib

# Asegura que 'common' esté en PYTHONPATH
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from common.soa_formatter import soa_formatter

ESB_HOST, ESB_PORT = "localhost", 5001

def send(service: str, payload: dict | str):
    raw = json.dumps(payload) if isinstance(payload, dict) else payload
    with socket.create_connection((ESB_HOST, ESB_PORT)) as s:
        s.sendall(soa_formatter(service, raw))
        length = int(s.recv(5))
        data = s.recv(length)
        print(data.decode()[7:])  # strip service code

# ---------------- CLI ----------------
parser = argparse.ArgumentParser(prog="soa-client", description="Cliente de prueba WMS-SOA")
sub = parser.add_subparsers(dest="cmd", required=True)

# Producto
p_prod = sub.add_parser("product")
p_prod_sub = p_prod.add_subparsers(dest="act", required=True)
p_create = p_prod_sub.add_parser("create")
p_create.add_argument("--nombre", required=True)
p_create.add_argument("--tam", type=float, required=True)
p_create.add_argument("--peso", type=float, required=True)
p_create.add_argument("--cat", required=True)
p_create.add_argument("--rot", required=True)
p_list = p_prod_sub.add_parser("list")

# Ubicación
p_loc = sub.add_parser("location")
p_loc_sub = p_loc.add_subparsers(dest="act", required=True)
p_loc_create = p_loc_sub.add_parser("create")
p_loc_create.add_argument("--codigo", required=True)
p_loc_create.add_argument("--cap", type=float, required=True)
p_loc_sub.add_parser("list")

# Movimiento
p_move = sub.add_parser("move")
p_move.add_argument("--prod", type=int, required=True)
p_move.add_argument("--src", type=int, required=True)
p_move.add_argument("--dst", type=int, required=True)
p_move.add_argument("--qty", type=int, required=True)

# Optimización
p_opt = sub.add_parser("optimize")
p_opt_sub = p_opt.add_subparsers(dest="act", required=True)
p_opt_suggest = p_opt_sub.add_parser("suggest")
p_opt_suggest.add_argument("--prod", type=int, required=True)
p_opt_suggest.add_argument("--qty", type=int, required=True)

# Visualización
p_viz = sub.add_parser("viz")
p_viz_sub = p_viz.add_subparsers(dest="act", required=True)
p_viz_sub.add_parser("map")
p_search = p_viz_sub.add_parser("search")
p_search.add_argument("--term", required=True)

# Alertas / Reportes
p_alert = sub.add_parser("alert")
p_alert_sub = p_alert.add_subparsers(dest="act", required=True)
p_low = p_alert_sub.add_parser("low")
p_low.add_argument("--thr", type=int, default=5)
p_alert_sub.add_parser("eff")

# Pedidos
p_order = sub.add_parser("order")
p_order_sub = p_order.add_subparsers(dest="act", required=True)
p_order_create = p_order_sub.add_parser("create")
p_order_create.add_argument("--items", required=True,
                            help="Formato id:cant,id:cant ... ej. '1:2,3:5'")
p_status = p_order_sub.add_parser("status")
p_status.add_argument("--id", type=int, required=True)

args = parser.parse_args()

# --------------- dispatch ----------------
if args.cmd == "product":
    if args.act == "create":
        payload = {"action": "create", "product": {
            "nombre": args.nombre,
            "tamanio": args.tam,
            "peso": args.peso,
            "categoria": args.cat,
            "rotacion": args.rot
        }}
    else:  # list
        payload = {"action": "list"}
    send("product_service", payload)

elif args.cmd == "location":
    if args.act == "create":
        payload = {"action": "create", "location": {
            "codigo": args.codigo,
            "capacidad": args.cap
        }}
    else:
        payload = {"action": "list"}
    send("location_service", payload)

elif args.cmd == "move":
    payload = {"action": "move", "product_id": args.prod,
               "from": args.src, "to": args.dst, "qty": args.qty}
    send("movement_service", payload)

elif args.cmd == "optimize" and args.act == "suggest":
    payload = {"action": "suggest", "product_id": args.prod, "qty": args.qty}
    send("optimization_service", payload)

elif args.cmd == "viz":
    if args.act == "map":
        send("visualization_service", {"action": "map"})
    else:  # search
        send("visualization_service", {"action": "search", "term": args.term})

elif args.cmd == "alert":
    if args.act == "low":
        send("alert_report_service", {"action": "low_stock", "threshold": args.thr})
    else:
        send("alert_report_service", {"action": "efficiency"})

elif args.cmd == "order":
    if args.act == "create":
        items = [{"id_producto": int(p.split(":")[0]),
                  "cantidad": int(p.split(":")[1])}
                 for p in args.items.split(",")]
        send("order_service", {"action": "create", "items": items})
    else:
        send("order_service", {"action": "status", "order_id": args.id})