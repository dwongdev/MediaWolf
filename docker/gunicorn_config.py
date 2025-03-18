import os

port = os.getenv("internal_port", 5000)

bind = f"0.0.0.0:{port}"
workers = 1
threads = 4
timeout = 180
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"
