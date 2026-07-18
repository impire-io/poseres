"""``pra-dash`` — the dashboard console entry point (feature 015).

Connects to a NATS server (the real transport, behind the B6 lazy-import
error), discovers live runs, and serves the dashboard page on localhost.
"""

from __future__ import annotations

import argparse
import sys
import time

__all__ = ["main"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pra-dash", description="One dashboard for any live PRA brain."
    )
    parser.add_argument("--url", default="nats://127.0.0.1:4222", help="NATS server URL")
    parser.add_argument("--port", type=int, default=8600, help="HTTP port (0 = ephemeral)")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="bind address — beyond localhost is your explicit choice",
    )
    args = parser.parse_args(argv)

    from pra.dash import DashboardModel, start_dashboard
    from pra.nats import NatsTransport  # raises the poseres[nats] message if absent

    transport = NatsTransport(args.url)
    model = DashboardModel(transport)
    model.start()
    server, url = start_dashboard(model, port=args.port, host=args.host)
    print(f"dashboard: {url}  (watching {args.url})", flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
        model.stop()
        transport.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
