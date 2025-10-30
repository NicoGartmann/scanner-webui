from flask import Flask, render_template_string, jsonify
import subprocess, time, os

app = Flask(__name__)

SCAN_DIR = "/app/scan"      # Fertige PDFs (Einzel + Mehrseitig)
TMP_DIR = "/app/tmp"        # Temporäre Dateien für Mehrseitenscan
DEVICE = "pixma:MG3600_Drucker"

# Verzeichnisse sicherstellen
os.makedirs(SCAN_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

# Zwischenspeicher für Mehrseiten-Scan
temp_scans = []

# Standard-Scanparameter für Dokumente
SCAN_PARAMS = [
    "--format=tiff",
    "--resolution", "300",
    "--mode", "Gray",
    "-x", "210",   # DIN A4 Breite in mm
    "-y", "297"    # DIN A4 Höhe in mm
]

HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>📠 Canon Scanserver</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.css">
    <style>
        body { display: flex; justify-content: center; align-items: center; height: 100vh; background: #f8f9fa; }
        .card { padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center; }
        #loading { display: none; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>📠 Canon Scanserver</h2>
        <button id="singleBtn" class="btn btn-primary mt-3">Einzel-Scan</button>
        <button id="multiBtn" class="btn btn-secondary mt-3">Mehrseitiger Scan</button>
        <div id="multiControls" style="display:none; margin-top:20px;">
            <button id="nextPageBtn" class="btn btn-info">Nächste Seite</button>
            <button id="finishBtn" class="btn btn-success">Fertigstellen</button>
        </div>
        <div id="loading" class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Scanning...</span>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js"></script>
    <script>
        function showToast(type, msg, title) {
            toastr.options = { "closeButton": true, "progressBar": true, "positionClass": "toast-top-center", "timeOut": "5000" };
            toastr[type](msg, title);
        }

        function startScan(url) {
            var loading = document.getElementById("loading");
            loading.style.display = "inline-block";

            fetch(url, { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    loading.style.display = "none";
                    if (data.success) { showToast("success", data.message, "Erfolg"); }
                    else { showToast("error", data.message, "Fehler"); }
                })
                .catch(err => {
                    loading.style.display = "none";
                    showToast("error", "Unerwarteter Fehler: " + err, "Fehler");
                });
        }

        document.getElementById("singleBtn").addEventListener("click", function() {
            startScan("/scan/single");
        });

        document.getElementById("multiBtn").addEventListener("click", function() {
            document.getElementById("multiControls").style.display = "block";
            showToast("info", "Mehrseitiger Scan gestartet. Scanne erste Seite...", "Info");
            startScan("/scan/page");
        });

        document.getElementById("nextPageBtn").addEventListener("click", function() {
            startScan("/scan/page");
        });

        document.getElementById("finishBtn").addEventListener("click", function() {
            startScan("/scan/finish");
            document.getElementById("multiControls").style.display = "none";
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/scan/single", methods=["POST"])
def single_scan():
    ts = time.strftime("%Y%m%d_%H%M%S")
    filename = f"scan_{ts}.pdf"
    filepath = os.path.join(SCAN_DIR, filename)
    return run_scan(filepath)

@app.route("/scan/page", methods=["POST"])
def scan_page():
    ts = time.strftime("%Y%m%d_%H%M%S")
    tmpfile = os.path.join(TMP_DIR, f"page_{len(temp_scans)+1}_{ts}.tiff")
    try:
        with open(tmpfile, "wb") as f:
            subprocess.run(
                ["scanimage", "--device-name", DEVICE, *SCAN_PARAMS],
                check=True, stdout=f
            )
        temp_scans.append(tmpfile)
        return jsonify(success=True, message=f"Seite {len(temp_scans)} gescannt")
    except subprocess.CalledProcessError as e:
        return jsonify(success=False, message=f"Scan fehlgeschlagen: {e}")

@app.route("/scan/finish", methods=["POST"])
def finish_scan():
    if not temp_scans:
        return jsonify(success=False, message="Keine Seiten vorhanden")

    ts = time.strftime("%Y%m%d_%H%M%S")
    filename = f"multiscan_{ts}.pdf"
    filepath = os.path.join(SCAN_DIR, filename)

    pdfs = []
    try:
        # TIFF -> PDF für jede Seite
        for i, tmpfile in enumerate(temp_scans, start=1):
            pdftmp = os.path.join(TMP_DIR, f"page_{i}.pdf")
            subprocess.run(["tiff2pdf", "-o", pdftmp, tmpfile], check=True)
            pdfs.append(pdftmp)

        # Zusammenführen aller PDFs
        subprocess.run(["pdfunite", *pdfs, filepath], check=True)

        return jsonify(success=True, message=f"Mehrseitiges PDF gespeichert als {filename}")

    except subprocess.CalledProcessError as e:
        return jsonify(success=False, message=f"Fehler beim Zusammenfügen: {e}")

    finally:
        # Cleanup aller temporären Dateien
        for f in temp_scans + pdfs:
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
        temp_scans.clear()

def run_scan(filepath):
    try:
        tifffile = filepath.replace(".pdf", ".tiff")
        with open(tifffile, "wb") as f:
            subprocess.run(
                ["scanimage", "--device-name", DEVICE, *SCAN_PARAMS],
                check=True, stdout=f
            )
        subprocess.run(["tiff2pdf", "-o", filepath, tifffile], check=True)
        os.remove(tifffile)
        return jsonify(success=True, message=f"Scan gespeichert als {os.path.basename(filepath)}")
    except subprocess.CalledProcessError as e:
        return jsonify(success=False, message=f"Scan fehlgeschlagen: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

