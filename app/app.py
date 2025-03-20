from flask import Flask, request
import socket
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Get the client's IP address
    client_ip = request.host.split(':')[0]

    # Get the server's hostname
    server_hostname = socket.gethostname()

    return f'Client IP: {client_ip}, Server Hostname: {server_hostname}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
