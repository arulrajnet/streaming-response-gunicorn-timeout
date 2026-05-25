import os

bind = "0.0.0.0:" + os.environ.get("PORT", "5001")
backlog = 2048

workers = int(os.environ.get("GUNICORN_WORKERS", "2"))
worker_class = "gevent"
worker_connections = 1000

# The bug-reproducer knob: gunicorn's worker timeout is 30s, the
# stream below will keep yielding until 40s so we cross the threshold.
timeout = 30
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = "info"

proc_name = "stream_repro"


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal (pid: %s)", worker.pid)


def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal (pid: %s)", worker.pid)
