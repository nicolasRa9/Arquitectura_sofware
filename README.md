# WMS SOA — Socket‑Based Scaffold

**Generated:** 2025-06-14T01:07:36.070495 UTC

## Concept

This scaffold implements a Service‑Oriented Architecture where *all* inter‑service communication occurs through a lightweight **10‑byte message bus** instead of HTTP APIs.

* **Bus Service (`bus_service`)** – acts as a simple TCP relay. Every message is exactly 10 bytes.  
* **Micro‑services** – seven domain‑specific services. Each connects to the bus, sends a 10‑byte heartbeat every 5 seconds, and logs any frame it receives.

## Running

```bash
docker compose up --build
```

* The bus listens on **port 9000**.  
* Services depend on the bus and start automatically.

## Extending

* Replace the `send_loop` implementation to publish domain events (e.g., `"PRD|000123"` for *product created*), always padding/truncating to 10 bytes.
* Parse incoming 10‑byte frames in `recv_loop` to trigger business logic.
* If you need *external* access, expose a separate API gateway but keep **internal** traffic on the socket bus to satisfy the “no‑HTTP” requirement.
