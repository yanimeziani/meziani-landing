FROM python:3.11.9

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install dependencies first (for better caching)
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install flask  # Add Flask for the dashboard

# Set the PYTHONPATH to include src/
ENV PYTHONPATH=/app/src

# Create data directory for memory DB storage
RUN mkdir -p /app/data && chmod 777 /app/data

# Copy the application code
COPY . .

# Create a simple Flask app for the dashboard
RUN echo 'from flask import Flask, render_template_string, jsonify\n\
import os\n\
import threading\n\
import json\n\
from datetime import datetime\n\
\n\
app = Flask(__name__)\n\
results = {"last_run": None, "status": "idle", "output": ""}\n\
\n\
def run_crew_task():\n\
    global results\n\
    results["status"] = "running"\n\
    try:\n\
        from media.main import run\n\
        output = run()\n\
        results["output"] = output or "Completed successfully"\n\
        results["status"] = "completed"\n\
        results["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")\n\
    except Exception as e:\n\
        results["status"] = "error"\n\
        results["output"] = str(e)\n\
\n\
@app.route("/")\n\
def home():\n\
    html = """\n\
    <!DOCTYPE html>\n\
    <html>\n\
    <head>\n\
        <title>CrewAI Dashboard</title>\n\
        <style>\n\
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }\n\
            h1 { color: #333; }\n\
            .card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; }\n\
            .status { font-weight: bold; }\n\
            .idle { color: #888; }\n\
            .running { color: #0066cc; }\n\
            .completed { color: #4CAF50; }\n\
            .error { color: #f44336; }\n\
            button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; \n\
                    border-radius: 4px; cursor: pointer; font-size: 16px; }\n\
            button:hover { background-color: #45a049; }\n\
            button:disabled { background-color: #cccccc; cursor: not-allowed; }\n\
            pre { background-color: #f5f5f5; padding: 15px; border-radius: 4px; overflow: auto; }\n\
        </style>\n\
    </head>\n\
    <body>\n\
        <h1>CrewAI Dashboard</h1>\n\
        \n\
        <div class="card">\n\
            <h2>Media Crew Status</h2>\n\
            <p>Status: <span id="status" class="status"></span></p>\n\
            <p>Last Run: <span id="lastRun"></span></p>\n\
            <button id="runButton" onclick="runCrew()">Run Media Crew</button>\n\
        </div>\n\
        \n\
        <div class="card">\n\
            <h2>Output</h2>\n\
            <pre id="output"></pre>\n\
        </div>\n\
        \n\
        <script>\n\
        function updateStatus() {\n\
            fetch("/status")\n\
                .then(response => response.json())\n\
                .then(data => {\n\
                    document.getElementById("status").textContent = data.status;\n\
                    document.getElementById("status").className = "status " + data.status;\n\
                    document.getElementById("lastRun").textContent = data.last_run || "Never";\n\
                    document.getElementById("output").textContent = data.output || "";\n\
                    \n\
                    const runButton = document.getElementById("runButton");\n\
                    if (data.status === "running") {\n\
                        runButton.disabled = true;\n\
                        runButton.textContent = "Running...";\n\
                    } else {\n\
                        runButton.disabled = false;\n\
                        runButton.textContent = "Run Media Crew";\n\
                    }\n\
                });\n\
        }\n\
        \n\
        function runCrew() {\n\
            fetch("/run-crew")\n\
                .then(response => response.json())\n\
                .then(data => {\n\
                    updateStatus();\n\
                });\n\
        }\n\
        \n\
        // Update status initially and every 2 seconds\n\
        updateStatus();\n\
        setInterval(updateStatus, 2000);\n\
        </script>\n\
    </body>\n\
    </html>\n\
    """\n\
    return render_template_string(html)\n\
\n\
@app.route("/run-crew")\n\
def run_crew():\n\
    global results\n\
    if results["status"] != "running":\n\
        thread = threading.Thread(target=run_crew_task)\n\
        thread.daemon = True\n\
        thread.start()\n\
        return jsonify({"success": True, "message": "Crew started"})\n\
    return jsonify({"success": False, "message": "Crew is already running"})\n\
\n\
@app.route("/status")\n\
def status():\n\
    return jsonify(results)\n\
\n\
if __name__ == "__main__":\n\
    app.run(host="0.0.0.0", port=5000, debug=False)\n\
' > src/app.py

# Expose the app port
EXPOSE 5000

# Run the Flask application
CMD ["python", "src/app.py"]