import os
import sys
import time
import platform
import psutil
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template

app = Flask(__name__)
START_TIME = time.time()


def uptime_str():
    seconds = int(time.time() - START_TIME)
    h, rem = divmod(seconds, 3600)
    m, s   = divmod(rem, 60)
    return f"{h}h {m}m {s}s"


def get_disk():
    """Return disk usage for the root path — works on Windows and Linux."""
    path = "C:\\" if sys.platform == "win32" else "/"
    return psutil.disk_usage(path)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/api/status")
def api_status():
    cpu  = psutil.cpu_percent(interval=0.2)
    mem  = psutil.virtual_memory()
    disk = get_disk()

    return jsonify({
        "status":    "online",
        "uptime":    uptime_str(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system": {
            "os":       platform.system(),
            "python":   platform.python_version(),
            "hostname": platform.node(),
        },
        "cpu_percent": cpu,
        "memory": {
            "total_mb": round(mem.total / 1024 / 1024, 1),
            "used_mb":  round(mem.used  / 1024 / 1024, 1),
            "percent":  mem.percent,
        },
        "disk": {
            "total_gb": round(disk.total / 1024 / 1024 / 1024, 1),
            "used_gb":  round(disk.used  / 1024 / 1024 / 1024, 1),
            "percent":  disk.percent,
        },
        "deployment": {
            "env":     os.environ.get("FLASK_ENV", "development"),
            "version": os.environ.get("APP_VERSION", "1.0.0"),
            "region":  os.environ.get("AWS_REGION",  "local"),
        },
    })

# Run the app on all interfaces, port 5000, with debug mode on for development.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)