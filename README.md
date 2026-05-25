# streaming-response-gunicorn-timeout

Minimal reproducer to check whether a Flask streaming response keeps a
gunicorn `gevent` worker alive past its configured `timeout`.

## Setup

| Knob | Value |
| --- | --- |
| Python | 3.11 |
| Flask | 2.3.3 |
| gunicorn | 22.0.0 |
| gevent | 24.2.1 |
| worker class | `gevent` |
| worker timeout | **30 s** |
| stream duration | **40 s** (timeout + 10 s) |
| yield interval | 500 ms |
| response `Content-Type` | `application/octet-stream` |

Versions and the gunicorn config style mirror
`~/workspace/otarepo/src/apigw/janusviewer`.

## Run

```bash
docker compose up --build
```

Then open <http://localhost:5001> and click **Start streaming download**.
The link uses `target="_blank"`, so the browser will handle it as a
download of `stream.bin`.

## What to look for

- Watch container logs: `docker compose logs -f`.
- The endpoint logs each chunk yield (`stream: yield chunk=N elapsed=…`).
- If the stream completes successfully you will see:
  `stream: finished after 40.xx s chunks=80 bytes=81920`.
- If gunicorn kills the worker at the 30 s mark you will instead see a
  `WORKER TIMEOUT` log line from gunicorn and the download will be
  truncated before the 40 s mark.

## Files

- `app.py` – Flask app with `/stream` endpoint.
- `gunicorn_config.py` – gunicorn config (`gevent`, `timeout = 30`).
- `templates/index.html` – HTML launcher with `target="_blank"` link.
- `Dockerfile` / `docker-compose.yml` – container setup.
