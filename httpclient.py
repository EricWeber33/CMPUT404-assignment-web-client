#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    USER_AGENT = "assign2_edweber/1.0"

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        try:
            return int(data.split("\r\n")[0].split()[1])
        except Exception:
            raise Exception("non-valid response code")

    def get_headers(self, data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
  
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    
    def parse_request_url(self, url):
        """
        @param: url: the full url requested

        @return: Tuple: a tuple containing the hostm followed by the resource
                requested
        """
        res = urllib.parse.urlparse(url)
        if res.scheme != "http":
            raise Exception("url scheme invalid: ", res.scheme)
        host = res.netloc
        port = 80
        resource = res.path or "/"
        if ":" in res.netloc:
            host, port = res.netloc.split(":")
        return (host, int(port), resource)

    def parse_response(self, resp):
        try:
            code = self.get_code(resp)
            headers = self.get_headers(resp) + "\r\n"
            body = self.get_body(resp)
        except Exception:
            code = 500
            headers = ""
            body = ""
        finally:
            return (code, headers, body)

    def make_headers(self, host, resource, post=False, content_length = None):
        method = "POST" if post else "GET"
        request = f"{method} {resource} HTTP/1.1\r\n" \
                  f"Host: {host}\r\n" \
                  "Connection: close\r\n" \
                  "Accept: */*\r\n" \
                  "Accept-Encoding: */*\r\n" \
                 f"User-Agent: {self.USER_AGENT}\r\n"
        if post:
            request += "Content-Type: application/x-www-form-urlencoded\r\n"
        if not content_length == None:
            request += f"Content-Length: {content_length}\r\n"
        request += "\r\n"
        return request

    def GET(self, url, args=None):
        host, port, resource = self.parse_request_url(url)
        self.connect(host, port)
        request = self.make_headers(host, resource)
        self.sendall(request)
        code, headers, body = self.parse_response(self.recvall(self.socket))
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        host, port, resource = self.parse_request_url(url)
        try:
            post_body =  urllib.parse.urlencode(args)
        except Exception:
            post_body = ""
        content_length = len(post_body)
        self.connect(host, port)
        request = self.make_headers(host, resource, post=True, content_length=content_length)
        request += post_body
        request += "\r\n\r\n"
        self.sendall(request)
        code, headers, body = self.parse_response(self.recvall(self.socket))
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
