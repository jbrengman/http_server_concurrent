import os
import mimetypes


def main(connection, address):
    try:
        message = receive(connection)
        handle(message, connection)
    finally:
        connection.close()


def receive(connection):
    message = ''
    while True:
        buffer = connection.recv(1024)
        if (buffer):
            message += buffer
        if (len(buffer) <= 1024):
            return message


def handle(message, connection):
    method, uri = process_request(message)
    try:
        check_method(method)
    except ValueError:
        response = build_response(
            '405 Method not allowed', '', '405 Method not allowed')
        send_response(response, connection)
    else:
        try:
            content, mimetype = get_content(uri)
        except ValueError:
            response = build_response('404 Not found', '', '404 Not found')
            send_response(response, connection)
        else:
            response = build_response('200 OK', mimetype, content)
            send_response(response, connection)


def process_request(message):
    first_line = message.split('\r\n')[0]
    split = first_line.split(' ')
    method = split[0]
    uri = split[1]
    return method, uri


def check_method(m):
    if (m == 'GET'):
        return True
    else:
        raise ValueError('Invalid method')


def get_content(uri):
    path = os.getcwd() + '/webroot' + uri
    if (os.path.isdir(path)):
        content = '\r\n'.join(os.listdir(path))
        mimetype = '\r\nContent-Type: text/plain'
    elif (os.path.isfile(path)):
        mimetype = '\r\nContent-Type: ' + mimetypes.guess_type(uri)[0]
        with open(path, 'rb') as infile:
            content = infile.read()
    else:
        raise ValueError('404 File not found')
    return content, mimetype


def build_response(message, mimetype, content):
    return ('HTTP/1.1 ' + message + mimetype + '\r\n\r\n' + content)


def send_response(response, connection):
    connection.sendall(response)

if __name__ == '__main__':
    from gevent.server import StreamServer
    from gevent.monkey import patch_all
    patch_all()
    server = StreamServer(('127.0.0.1', 50000), main)
    print('Starting http server on port 50000')
    server.serve_forever()
