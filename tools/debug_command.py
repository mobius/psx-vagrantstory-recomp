"""Send one JSON command to the project's loopback debug port."""
import json
import argparse
import socket
import sys

parser = argparse.ArgumentParser()
parser.add_argument('request')
parser.add_argument('--port', type=int, default=18765)
args = parser.parse_args()
request = json.loads(args.request)
with socket.create_connection(('127.0.0.1', args.port), timeout=8) as connection:
    connection.sendall((json.dumps(request) + '\n').encode())
    response = bytearray()
    while chunk := connection.recv(65536):
        response.extend(chunk)
print(response.decode(errors='replace'))
