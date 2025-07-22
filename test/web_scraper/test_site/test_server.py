# test_server.py
from flask import Flask, send_from_directory
app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    """
    Serve the index.html file from the current directory.
    """
    return send_from_directory('.', 'index.html')

@app.route('/img/<path:filename>')
def images(filename):
    """
    Serve images from the 'img' directory.
    """
    return send_from_directory('img', filename)

if __name__ == '__main__':
    app.run(port=8000)
