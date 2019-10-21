import socket
import sys
import traceback
import os
import mimetypes


def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    Ex:
        response_ok(
            b"<html><h1>Welcome:</h1></html>",
            b"text/html"
        ) ->

        b'''
        HTTP/1.1 200 OK\r\n
        Content-Type: text/htm l\r\n
        \r\n
        <html><h1>Welcome:</h1></html>\r\n
        '''
    """
    retval = "HTTP/1.1 200 OK\r\ncontent-type: {0}\r\n".format(
        mimetype).encode()
    if mimetype != None and mimetype != b"text/plain" and "image" in mimetype:
        retval += "Accept-Ranges: bytes\r\n\r\n".encode()
    retval += body
    return retval


def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""

    # TODO: Implement response_method_not_allowed
    # Connection: close\r\n<!DOCTYPE html><html><body><h1>405 Method not allowed</h1></body></html>".encode()
    return "HTTP/1.1 405 Method Not Allowed\r\n".encode()


def response_not_found():
    """Returns a 404 Not Found response"""

    # TODO: Implement response_not_found
    #return "HTTP/1.1 404 Not Found\r\n".encode()#Connection: close\r\n<!DOCTYPE html><html><body><h1>404 Not found</h1></body></html>".encode()
    return "HTTP/1.1 404 Not Found\r\nServer: Varnish\r\ncontent-type: text/html\r\nAccept-Ranges: bytes\r\nConnection: close\r\n<html><body><h1>404 Not found</h1></body></html>".encode()


def parse_request(request):
    """
    Given the content of an HTTP request, returns the path of that request.

    This server only handles GET requests, so this method shall raise a
    NotImplementedError if the method of the request is not GET.
    """
    lines = request.split("\n")
    firstLine = lines[0].split()
    requestType = firstLine[0]

    if requestType != "GET":
        raise NotImplementedError(f"{requestType} request not supported!")
    path = firstLine[1]

    return path


def response_path(path):
    """
    This method should return appropriate content and a mime type.

    If the requested path is a directory, then the content should be a
    plain-text listing of the contents with mimetype `text/plain`.

    If the path is a file, it should return the contents of that file
    and its correct mimetype.

    If the path does not map to a real location, it should raise an
    exception that the server can catch to return a 404 response.

    Ex:
        response_path('/a_web_page.html') -> (b"<html><h1>North Carolina...",
                                            b"text/html")

        response_path('/images/sample_1.png')
                        -> (b"A12BCF...",  # contents of sample_1.png
                            b"image/png")

        response_path('/') -> (b"images/, a_web_page.html, make_type.py,...",
                             b"text/plain")

        response_path('/a_page_that_doesnt_exist.html') -> Raises a NameError

    """

    # Get all the files in webroot that can be accessed
    files = []
    for dirPath, dirNames, fileNames in os.walk("webroot"):
        for fileName in fileNames:
            files.append(os.path.join(dirPath, fileName)[
                         len("webroot"):].replace("\\", "/"))

    # TODO: Fill in the appropriate content and mime_type give the path.
    # See the assignment guidelines for help on "mapping mime-types", though
    # you might need to create a special case for handling make_time.py
    #
    # If the path is "make_time.py", then you may OPTIONALLY return the
    # result of executing `make_time.py`. But you need only return the
    # CONTENTS of `make_time.py`.

    content = b"no such file"
    if path == "/":
        content = "<!DOCTYPE html>\r\n<html>\r\n<body>\r\n\r\n<h1>Welcome</h1>\r\n\r\n<p>{0}</p>\r\n\r\n</body>\r\n</html>\r\n\r\n".format(
            "</p>\r\n<p>".join(files)).encode()
        #content = "<!DOCTYPE html>\r\n<html>\r\n<body>\r\n\r\n<h1>North Carolina</h1>\r\n\r\n<p>A fine place to spend a week learning web programming!</p>\r\n\r\n</body>\r\n</html>\r\n\r\n".encode()
        mime_type = "text/html"
    elif path not in files:
        raise NameError(f"No such path {path}")
    else:
        with open("webroot" + path, mode="rb") as f:
            content = f.read()
            mime_type = mimetypes.guess_type(path)[0]

    return content, mime_type


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            conn.settimeout(3)
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if not request or '\r\n\r\n' in request:
                        break

                print("Request received:\n{}\n\n".format(request))

                # TODO: Use parse_request to retrieve the path from the request.
                path = parse_request(request)

                # TODO: Use response_path to retrieve the content and the mimetype,
                # based on the request path.
                response = b""
                try:
                    body, mime = response_path(path)
                    response = response_ok(
                        body=body,
                        mimetype=mime
                    )
                except NotImplementedError:
                    response = response_method_not_allowed()
                except NameError:
                    response = response_not_found()

                conn.sendall(response)
            except:
                traceback.print_exc()
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)
