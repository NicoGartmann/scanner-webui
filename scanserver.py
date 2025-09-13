from flask import Flask, render_template_string, jsonify
import subprocess, time, os

app = Flask(__name__)

SCAN_DIR = "/app/scan"
DEVICE = "pixma:MG3600_series"

HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>📠 Canon Scanserver</title>
    <!-- Bootstrap -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <!-- Toastr -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.css">
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: #f8f9fa;
        }
        .card {
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            text-align: center;
        }
        #loading {
            display: none;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>📠 Canon Scanserver</h2>
        <button id="scanBtn" class="btn btn-primary mt-3">Scan starten</button>
        <div id="loading" class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Scanning...</span>
        </div>
    </div>

    <!-- JS Libs -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js"></script>
    <script>
        document.getElementById("scanBtn").addEventListener("click", function() {
            var loading = document.getElementById("loading");
            loading.style.display = "inline-block";

            fetch("/scan", { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    loading.style.display = "none";
                    if (data.success) {
                        toastr.success(data.message, "Erfolg");
                    } else {
                        toastr.error(data.message, "Fehler");
                    }
                })
                .catch(err => {
                    loading.style.display = "none";
                    toastr.error("Beim Scannen ist etwas schief gelaufen", "Fehler");
                });
        });

        toastr.options = {
            "closeButton": true,
            "progressBar": true,
            "positionClass": "toast-top-center",
            "timeOut": "5000"
        };
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/scan", methods=["POST"])
def scan():
    ts = time.strftime("%Y%m%d_%H%M%S")
    filename = f"scan_{ts}.pdf"
    filepath = os.path.join(SCAN_DIR, filename)

    cmd = f'scanimage --device-name="{DEVICE}" --format=pnm | pnmtops | ps2pdf - "{filepath}"'
    try:
        subprocess.run(cmd, shell=True, check=True)
        return jsonify(success=True, message=f"Scan gespeichert als {filename}")
    except subprocess.CalledProcessError as e:
        return jsonify(success=False, message=f"Beim Scannen ist etwas schief gelaufen")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
