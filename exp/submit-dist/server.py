#!/usr/bin/env python3

from logging import getLogger, basicConfig, INFO
from argparse import ArgumentParser
from http.server import HTTPServer, BaseHTTPRequestHandler

log = getLogger()

def main(args):
    log.info("Listening on {}:{}".format(args.ip, args.port))
    server = HTTPServer((args.ip, args.port), Handler)
    server.serve_forever()

def get_args():
    parser = ArgumentParser(description="Server that echos POSTed length")
    parser.add_argument("--ip", "-i", type=str, default="localhost",
        help="Server IP address")
    parser.add_argument("--port", "-p", type=int, default=8080,
        help="Server port")
    return parser.parse_args()

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("{}".format(
            int(self.headers["Content-Length"])).encode("UTF-8"),
        )

if __name__ == "__main__":
    basicConfig(
        format="[%(levelname)s] %(message)s",
        level = INFO,
    )
    main(get_args())
