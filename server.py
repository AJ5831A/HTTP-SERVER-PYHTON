import socket , os , sys 
from threading import Lock , Thread
from datetime import datetime , timezone

# CLI argument -> python server.py [port] [host] [max_threads]
PORT = 8080
HOST = '127.0.0.1'
MAX_THREADS = 10

if len(sys.argv)>1:
    PORT = sys.argv[1]
if len(sys.argv)>2:
    HOST = sys.argv[2]
if len(sys.argv)>3:
    MAX_THREADS = sys.argv[3]

BASE = os.path.abspath('resources')
UPLOADS = os.path.join(BASE , 'uploads')
os.makedirs(BASE , exist_ok = True)
os.makedirs(UPLOADS , exist_ok = True)

logLock = Lock()
def log(msg):
    with logLock:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{ts}] : {msg}" , flush=True)

def dateHdr():
    return datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

def buildHeaders(statusCode , statusMsg , headers = None , contentLen = 0 , contentType = 'text/html'):
    h = [
        f"HTTP/1.1 {statusCode} {statusCode}",
        f"Date: {dateHdr()}",
        f"Server: Multi-threaded HTTP server",
        f"Content type: {contentType}",
        f"Content length: {contentLen}"
    ]

    if headers:
        h.extend(headers)
    return "\r\n".join(h) + "\r\n\r\n" 

def errorPage(statusCode , statusMsg , desc):
    body = f"""
    <html>
    <head><title>{statusCode} {statusMsg}</title></head>
    <body>
    <h1>{statusCode} {statusMsg}</h1>
    <p>{desc}</p>
    <hr>
    <p><em>Multi-threaded HTTP Server</em></p>
    </body>
    </html>
    """
    return body

def safePathJoin(base , reqPath):
    p = reqPath.split('?' , 1)[0]
    p = p.lstrip('/')
    if p=='':
        p = 'index.html'
    target = os.path.abspath(os.path.join(base , p))
    baseAbs = os.path.abspath(base)
    if not target.startswith(baseAbs + os.sep) and target != baseAbs:
        return None
    return target


