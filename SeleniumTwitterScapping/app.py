from flask import Flask, render_template, jsonify
import subprocess
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script', methods=['GET'])
def run_script():
    result = subprocess.run(['python3', 'twitter_trending.py'], capture_output=True, text=True)
    
    # Print the raw output for debugging
    print(f"Raw output: {result.stdout}")
    
    try:
        result_json = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return jsonify({"error": "Failed to decode JSON", "details": str(e), "output": result.stdout}), 500
    
    return jsonify(result_json)

if __name__ == "__main__":
    app.run(debug=True)
