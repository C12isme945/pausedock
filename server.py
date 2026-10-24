"""Loopback-only, dependency-free web UI. Nothing is written to disk by requests."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import argparse,json,mimetypes,threading
from core import classify

PUBLIC=Path(__file__).resolve().parent/'public'
BUSY=threading.Lock()

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def safe_request(self):
        port=self.server.server_address[1]
        hosts={f'127.0.0.1:{port}',f'localhost:{port}'}
        if self.headers.get('Host') not in hosts:return False
        origin=self.headers.get('Origin')
        return origin is None or origin in {f'http://{h}' for h in hosts}
    def send(self,status,body,mime='application/json'):
        if not isinstance(body,bytes):body=json.dumps(body,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type',mime+('; charset=utf-8' if mime.startswith('text/') or mime=='application/json' else ''))
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers();self.wfile.write(body)
    def do_GET(self):
        if not self.safe_request():return self.send(403,{'error':'Only the local application can access this page.'})
        path=self.path.split('?',1)[0]
        allowed={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
        if path not in allowed:return self.send(404,{'error':'Page not found.'})
        file=PUBLIC/allowed[path]
        self.send(200,file.read_bytes(),mimetypes.guess_type(file.name)[0] or 'text/plain')
    def do_POST(self):
        if not self.safe_request():return self.send(403,{'error':'Requests must come from the local application.'})
        if self.path!='/api/park':return self.send(404,{'error':'Unknown action.'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.send(415,{'error':'Use JSON.'})
        try: length=int(self.headers.get('Content-Length','0'))
        except ValueError:return self.send(400,{'error':'Invalid request size.'})
        if not 0<length<=30000:return self.send(413,{'error':'These notes are too long.'})
        try:
            body=json.loads(self.rfile.read(length))
            if not isinstance(body,dict) or set(body)!={'notes'}:raise ValueError('Expected notes only.')
        except (ValueError,UnicodeDecodeError):return self.send(400,{'error':'The request could not be read.'})
        if not BUSY.acquire(blocking=False):return self.send(409,{'error':'A return card is already being made. Please wait.'})
        try:
            result=classify(body['notes']);self.send(200,result)
        except ValueError as exc:self.send(422,{'error':str(exc)})
        except RuntimeError as exc:self.send(503,{'error':str(exc)})
        except Exception:self.send(500,{'error':'The local run did not finish. Your notes are unchanged; please try again.'})
        finally:BUSY.release()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8768);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'PauseDock is ready at http://127.0.0.1:{args.port} (local device only)',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close()
