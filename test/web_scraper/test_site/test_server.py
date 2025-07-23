# test_server.py
from threading import Thread
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    """
    Serve the index.html file from the current directory.
    """
    return send_from_directory('.', 'index.html')

@app.route('/images/<path:filename>')
def images(filename):
    """
    Serve images from the 'img' directory.
    """
    return send_from_directory('images', filename)

def run_server(port=8000):
    """
    Start the Flask server in a separate thread.
    Returns the thread and the shutdown function.
    """
    from werkzeug.serving import make_server

    class ServerThread(Thread):
        def __init__(self, app, port):
            super().__init__()
            self.server = make_server('localhost', port, app)
            self.ctx = app.app_context()
            self.ctx.push()

        def run(self):
            self.server.serve_forever()

        def shutdown(self):
            self.server.shutdown()

    server_thread = ServerThread(app, port)
    server_thread.start()
    return server_thread
