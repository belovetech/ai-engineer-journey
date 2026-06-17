"""Tiny CORS proxy for ChromaDB's Rust frontend.

ChromaDB >= 1.x uses a Rust server that doesn't handle CORS preflight
requests. This proxy sits between the web UI and ChromaDB, adding the
necessary CORS headers.

Usage:
    # Terminal 1: start ChromaDB
    .venv/bin/chroma run --path week2/.chromadb --port 8000

    # Terminal 2: start this proxy
    python week2/chroma_proxy.py

    # Web UI: connect to http://localhost:8080 (not 8000)
"""

import requests
from flask import Flask, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CHROMA_URL = "http://localhost:8000"


@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def proxy(path):
    url = f"{CHROMA_URL}/{path}"
    resp = requests.request(
        method=request.method,
        url=url,
        headers={k: v for k, v in request.headers if k.lower() != "host"},
        data=request.get_data(),
        params=request.args,
    )
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("content-type"))


if __name__ == "__main__":
    print("CORS proxy listening on http://localhost:8080 -> http://localhost:8000")
    app.run(port=8080, debug=False)
