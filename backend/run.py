from app import socketio, app

if __name__ == "__main__":
    print("✅ Avvio server Flask-SocketIO con threading da run.py")
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
