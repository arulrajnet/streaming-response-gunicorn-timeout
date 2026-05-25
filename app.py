import logging
import os
import time

from flask import Flask, Response, render_template

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
)
log = logging.getLogger("streamapp")

app = Flask(__name__)

STREAM_DURATION_SEC = float(os.environ.get("STREAM_DURATION_SEC", "40"))
STREAM_INTERVAL_SEC = float(os.environ.get("STREAM_INTERVAL_SEC", "0.5"))
CHUNK_SIZE_BYTES = int(os.environ.get("CHUNK_SIZE_BYTES", "1024"))


@app.route("/")
def index():
    return render_template(
        "index.html",
        duration=STREAM_DURATION_SEC,
        interval=STREAM_INTERVAL_SEC,
        chunk_size=CHUNK_SIZE_BYTES,
    )


@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


@app.route("/stream")
def stream():
    start = time.monotonic()
    log.info("stream: started pid=%s", os.getpid())

    def generate():
        sent = 0
        index = 0
        while True:
            elapsed = time.monotonic() - start
            if elapsed >= STREAM_DURATION_SEC:
                log.info(
                    "stream: finished after %.2fs chunks=%d bytes=%d",
                    elapsed,
                    index,
                    sent,
                )
                return

            payload = (f"chunk={index:06d} elapsed={elapsed:7.3f}s ").encode("ascii")
            payload = payload.ljust(CHUNK_SIZE_BYTES, b"\0")
            sent += len(payload)
            index += 1
            log.info("stream: yield chunk=%d elapsed=%.3fs", index, elapsed)
            yield payload
            time.sleep(STREAM_INTERVAL_SEC)

    headers = {
        "Content-Type": "application/octet-stream",
        "Content-Disposition": 'attachment; filename="stream.bin"',
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "X-Accel-Buffering": "no",
    }
    return Response(generate(), headers=headers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
