from flask import Flask, render_template_string, jsonify, request
import os
import threading
import json
from datetime import datetime

app = Flask(__name__)
results = {"last_run": None, "status": "idle", "output": ""}

def run_crew_task(model=None):
    global results
    results["status"] = "running"
    results["output"] = "Starting crew with model: " + (model or os.environ.get('MODEL', 'claude-3-5-sonnet-20240620'))
    
    try:
        # Set the model in the environment
        if model:
            os.environ['MODEL'] = model
        
        # Clear OpenAI key to force Anthropic usage
        os.environ["OPENAI_API_KEY"] = ""
        
        from media.main import run
        output = run()
        results["output"] = output or "Completed successfully"
        results["status"] = "completed"
        results["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        results["status"] = "error"
        results["output"] = str(e)

@app.route("/")
def home():
    # Get available Anthropic models
    models = [
        "claude-3-5-sonnet-20240620",
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229"
    ]
    
    current_model = os.environ.get('MODEL', 'claude-3-5-sonnet-20240620')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CrewAI Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
            .status {{ font-weight: bold; }}
            .idle {{ color: #888; }}
            .running {{ color: #0066cc; }}
            .completed {{ color: #4CAF50; }}
            .error {{ color: #f44336; }}
            button {{ background-color: #4CAF50; color: white; padding: 10px 15px; border: none; 
                    border-radius: 4px; cursor: pointer; font-size: 16px; }}
            button:hover {{ background-color: #45a049; }}
            button:disabled {{ background-color: #cccccc; cursor: not-allowed; }}
            pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 4px; overflow: auto; }}
            select {{ padding: 8px; margin-right: 10px; font-size: 16px; }}
        </style>
    </head>
    <body>
        <h1>CrewAI Dashboard</h1>
        
        <div class="card">
            <h2>Media Crew Status</h2>
            <p>Status: <span id="status" class="status"></span></p>
            <p>Last Run: <span id="lastRun"></span></p>
            <p>
                <label for="modelSelect">Anthropic Model:</label>
                <select id="modelSelect">
                    {"".join(f'<option value="{model}" {"selected" if model == current_model else ""}>{model}</option>' for model in models)}
                </select>
                <button id="runButton" onclick="runCrew()">Run Media Crew</button>
            </p>
        </div>
        
        <div class="card">
            <h2>Configuration</h2>
            <p>ANTHROPIC_API_KEY: {os.environ.get('ANTHROPIC_API_KEY', 'Not set').replace(os.environ.get('ANTHROPIC_API_KEY', '')[4:] if os.environ.get('ANTHROPIC_API_KEY') else '', '********')}</p>
            <p>MODEL: <span id="currentModel">{current_model}</span></p>
        </div>
        
        <div class="card">
            <h2>Output</h2>
            <pre id="output"></pre>
        </div>
        
        <script>
        function updateStatus() {{
            fetch("/status")
                .then(response => response.json())
                .then(data => {{
                    document.getElementById("status").textContent = data.status;
                    document.getElementById("status").className = "status " + data.status;
                    document.getElementById("lastRun").textContent = data.last_run || "Never";
                    document.getElementById("output").textContent = data.output || "";
                    
                    const runButton = document.getElementById("runButton");
                    if (data.status === "running") {{
                        runButton.disabled = true;
                        runButton.textContent = "Running...";
                    }} else {{
                        runButton.disabled = false;
                        runButton.textContent = "Run Media Crew";
                    }}
                }});
        }}
        
        function runCrew() {{
            const model = document.getElementById("modelSelect").value;
            document.getElementById("currentModel").textContent = model;
            
            fetch("/run-crew?model=" + encodeURIComponent(model))
                .then(response => response.json())
                .then(data => {{
                    updateStatus();
                }});
        }}
        
        // Update status initially and every 2 seconds
        updateStatus();
        setInterval(updateStatus, 2000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/run-crew")
def run_crew():
    global results
    model = request.args.get('model')
    
    if results["status"] != "running":
        thread = threading.Thread(target=run_crew_task, args=(model,))
        thread.daemon = True
        thread.start()
        return jsonify({"success": True, "message": f"Crew started with model: {model}"})
    return jsonify({"success": False, "message": "Crew is already running"})

@app.route("/status")
def status():
    return jsonify(results)

if __name__ == "__main__":
    # Make sure we're using Anthropic
    os.environ["OPENAI_API_KEY"] = ""
    app.run(host="0.0.0.0", port=5000, debug=False)