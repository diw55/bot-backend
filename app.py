from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import subprocess
import os
import sys
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

bot_process = None

def read_bot_output(process):
    """อ่าน Log จากบอทแบบ Real-time"""
    for line in iter(process.stdout.readline, ''):
        if line:
            socketio.emit('bot_log', {'log': line.strip()})

@app.route('/')
def index():
    return "Bot Backend is Running."

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
    env["PYTHONUNBUFFERED"] = "1" # บังคับให้ Python พ่น Log ออกมาทันที
    
    bot_process = subprocess.Popen(
        [sys.executable, "dynamic_bot.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # เริ่ม Thread อ่าน Log
    threading.Thread(target=read_bot_output, args=(bot_process,), daemon=True).start()
    
    return jsonify({"status": "started", "message": "Bot Started"})

@app.route('/stop', methods=['POST'])
def stop_bot():
    global bot_process
    if bot_process and bot_process.poll() is None:
        bot_process.terminate()
        return jsonify({"status": "stopped"})
    return jsonify({"error": "Bot is not running"}), 400

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
