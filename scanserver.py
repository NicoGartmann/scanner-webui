from flask import Flask, send_file
import subprocess, time, os

SCAN_DIR = "/opt/paperless/consume"
DEVICE="pixma:MG3600_192.168.0.44"

app = Flask(__name__)

@app.route("/")
def index():
    return """
        <h1>Canon Scanserver</h1>
        <form action="/scan", method="post">
            <button type="submit">Scan starten</button>
        </form>
    """

@app.route("/scan", methods=["POST"])
def scan():
    ts = time.strftime("%Y%m%d_%H%M%S")
    filename = f"scan_{ts}.pdf"
    filepath = os.path.join(SCAN_DIR, filename)

    cmd = f'scanimage --device-name="{DEVICE}" --format=pnm | pnmtops | ps2pdf - "{filepath}"'
    subprocess.run(cmd, shell=True, check=True)

    return f"Scan gespeichert unter: {filepath}<br><a href='/'>Zurueck</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
