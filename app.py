from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import sys

app = Flask(__name__)
CORS(app)

bot_process = None

@app.route('/start', methods=['POST'])
def start_bot():
    global bot_process
    data = request.json
    token = data.get('token')
    code = data.get('code')
    
    if not token or not code:
        return jsonify({"error": "Missing token or code"}), 400
        
    if bot_process and bot_process.poll() is None:
        bot_process.terminate()
        bot_process.wait()

    with open("dynamic_bot.py", "w") as f:
        f.write(code)
    
    env = os.environ.copy()
    env["DISCORD_TOKEN"] = token
    
    bot_process = subprocess.Popen([sys.executable, "dynamic_bot.py"], env=env)
    
    return jsonify({"status": "started", "message": "Bot is starting..."})

@app.route('/stop', methods=['POST'])
def stop_bot():
    global bot_process
    if bot_process and bot_process.poll() is None:
        bot_process.terminate()
        bot_process.wait()
        return jsonify({"status": "stopped", "message": "Bot stopped."})
    return jsonify({"error": "Bot is not running"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
