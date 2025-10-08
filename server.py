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

def parseRequest(data):
    lines = data.split('\n')
    if not lines:
        return None
    firstLine = lines[0].split(' ')
    method , path , version = firstLine
    if len(firstLine)<3:
        return None
    
    headers = {}
    i = 1
    while i<len(lines) and lines[i]:
        line = lines[i]
        if ':' in line:
            k , v = line.split(':' , 1)
            headers[k.strip().lower()] = v.strip()
        i+=1
    body = '\r\n'.join(lines[i+1:]) if i+1 < len(lines) else ''
    return method , path , version , headers , body

def handelConnection(conn , addr):
    threadName = f"Thread-{addr[1]}"
    log(f"[{threadName}] Connection from {addr[0]}:{addr[1]}")
    conn.settimeout(30)
    requestsServed = 0
    keepAlive = True
    while keepAlive and requestsServed < 100:
        try:
            data = b""
            #read until header end
            while b"\r\n\r\n" not in data:
                chunck = conn.recv(4096)
                if not chunck:
                    raise ConnectionResetError
                data += chunck
                if len(data) > 8192:
                    break
                text = data.decode(errors = 'replace')
                parsed = parseRequest(text)
                if not parsed:
                    body = errorPage(400 , "Bad Request" , "Malformed request.")
                    hdr = buildHeaders(400 , "Bad Request" , contentLen=len(body.encode()))
                    conn.sendall((hdr+body).encode())
                    log(f"[{threadName}] Request: malformed -> 400")
                    break
                method , path , version , headers , bodyTail = parsed
                log(f"[{threadName}] Request: {method} {path} {version}")

                #Host header validatiom
                hostHDR = headers.get('host')
                exprectedHost = f"{HOST}:{PORT}"
                if not hostHDR:
                    body = errorPage(400 , "Bad Request" , "Missing host header.")
                    hdr = buildHeaders(400 , "Bad Request" , contentLen=len(body.encode()))
                    conn.sendall((hdr+body).encode())
                    log(f"[{threadName}] Host Missing -> 400")
                    break
                if hostHDR != exprectedHost and hostHDR != f"localhost:{PORT}" and hostHDR != f"127.0.0.1:{PORT}":
                    body = errorPage(403, "Forbidden", "Host header mismatch.")
                    hdr = buildHeaders(403, "Forbidden", content_len=len(body.encode()))
                    conn.sendall((hdr + body).encode())
                    log(f"[{threadName}] Host mismatch ({hostHDR}) -> 403")
                    break

                #Connection Header
                connHDR = headers.get('connection' , '').lower()
                if version == 'HTTP/1.0':
                    keepAlive = (connHDR == 'keep-alive')
                else:
                    keepAlive = (connHDR!='close')

                #handle GET
                if method.upper() == 'GET':
                    target = safePathJoin(BASE , path)
                    if not target:
                        body = errorPage(403 , "Forbidden" , "Access denied.")
                        hdr = buildHeaders(403 , "Forbidden" , contentLen=len(body.encode()))
                        conn.sendall((hdr+body).encode())
                        log(f"[{threadName}] -> 404 {target}")
                        continue
                    if not os.path.exists(target) or not os.path.isfile(target):
                        body = errorPage(404 , "Not Found" , "Resource not found.")
                        hdr = buildHeaders(404 , "Not Found" , contentLen=len(body.encode()))
                        conn.sendall((hdr+body).encode())
                        log(f"[{threadName}] -> 404 {target}")
                        continue
                    ext = os.path.splitext(target)[1].lower()
                    if ext in('.html' , '.htm'):
                        with open(target , 'r' , encodings = 'utf-8' , errors='replace') as f:
                            content = f.read().encode()
                        headersExtra = [f"Connection: {'keep-alive' if keepAlive else 'close'}" , f"Keep-Alive: timeout={30} , max={100}"]
                        hdr = buildHeaders(200 , "OK" , headers=headersExtra , contentLen=len(content) , contentType='text/html; charset=utf-8')
                        conn.sendall(hdr.encode() + content)
                        log(f"[{threadName}] Response: 200 OK {os.path.basename(target)} ({len(content)} bytes)")
                    elif ext in ('.png' , '.jpg' , '.jpeg' , '.txt'):
                        with open(target , 'rb') as f:
                            content = f.read()
                        headersExtra = [f"Content-Disposition: attachment; filename\"{os.path.basename(target)}\"" , f"Connection: {'keep-alive' if keepAlive else 'close'}"]
                        hdr = buildHeaders(200 , "OK" , headers=headersExtra , contentLen=len(content) , contentType='application/octet-stream')
                        conn.sendall(hdr.encode() + content)
                        log(f"[{threadName}] Response: 200 OK (binary) {os.path.basename(target)} ({len(content)} bytes)")
                    else:
                        body = errorPage(415 , "Unsupported Media Type" , "File type not supported.")
                        hdr = buildHeaders(415 , "Unsupported Media Type" , contentLen=len(body.encode()))
                        conn.sendall((hdr+body).encode())
                        log(f"[{threadName}] -> 415 {ext}")
        


