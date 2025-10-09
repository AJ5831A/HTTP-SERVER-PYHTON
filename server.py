import socket, os, sys, json, uuid
from threading import Lock, Thread
from datetime import datetime, timezone
from queue import Queue

# ------------------ Configuration ------------------ #
PORT = 8080
HOST = "127.0.0.1"
MAX_THREADS = 10
REQ_LIMIT_PER_CONN = 100
QUEUE_SIZE = 100
KEEPALIVE_TIMEOUT = 30

# CLI Arguments
if len(sys.argv) > 1:
    PORT = int(sys.argv[1])
if len(sys.argv) > 2:
    HOST = sys.argv[2]
if len(sys.argv) > 3:
    MAX_THREADS = int(sys.argv[3])

# Base directories
BASE = os.path.abspath("resources")
UPLOADS = os.path.join(BASE, "uploads")
os.makedirs(BASE, exist_ok=True)
os.makedirs(UPLOADS, exist_ok=True)

# ------------------ Utility Functions ------------------ #
logLock = Lock()
def log(msg):
    """Thread-safe logger"""
    with logLock:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] : {msg}", flush=True)

def dateHdr():
    """Return RFC 1123 formatted date"""
    return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

def buildHeaders(statusCode, statusMsg, headers=None, contentLen=0, contentType="text/html"):
    """Build proper HTTP response headers"""
    h = [
        f"HTTP/1.1 {statusCode} {statusMsg}",
        f"Date: {dateHdr()}",
        f"Server: Multi-threaded HTTP Server",
        f"Content-Type: {contentType}",
        f"Content-Length: {contentLen}",
    ]
    if headers:
        h.extend(headers)
    return "\r\n".join(h) + "\r\n\r\n"

def errorPage(statusCode, statusMsg, desc):
    """Generate a simple HTML error page"""
    return f"""
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

def safePathJoin(base, reqPath):
    """Safely join a request path with base directory"""
    p = reqPath.split("?", 1)[0]
    p = p.lstrip("/")
    if p == "":
        p = "index.html"
    target = os.path.abspath(os.path.join(base, p))
    baseAbs = os.path.abspath(base)
    if not target.startswith(baseAbs + os.sep) and target != baseAbs:
        return None
    return target

def parseRequest(data):
    """Parse raw HTTP request"""
    lines = data.split("\r\n")
    if not lines or len(lines[0].split(" ")) < 3:
        return None

    method, path, version = lines[0].split(" ", 2)
    headers = {}
    i = 1
    while i < len(lines) and lines[i]:
        if ":" in lines[i]:
            k, v = lines[i].split(":", 1)
            headers[k.strip().lower()] = v.strip()
        i += 1

    body = "\r\n".join(lines[i+1:]) if i + 1 < len(lines) else ""
    return method, path, version, headers, body

# ------------------ Connection Handler ------------------ #
def handleConnection(conn, addr):
    threadName = f"Thread-{addr[1]}"
    log(f"[{threadName}] Connection from {addr[0]}:{addr[1]}")

    conn.settimeout(KEEPALIVE_TIMEOUT)
    requestsServed = 0
    keepAlive = True

    while keepAlive and requestsServed < REQ_LIMIT_PER_CONN:
        try:
            data = b""
            while b"\r\n\r\n" not in data:
                chunk = conn.recv(4096)
                if not chunk:
                    raise ConnectionResetError
                data += chunk
                if len(data) > 8192:
                    break

            text = data.decode(errors="replace")
            parsed = parseRequest(text)
            if not parsed:
                body = errorPage(400, "Bad Request", "Malformed request.")
                hdr = buildHeaders(400, "Bad Request", contentLen=len(body.encode()))
                conn.sendall((hdr + body).encode())
                log(f"[{threadName}] Malformed request -> 400")
                break

            method, path, version, headers, bodyTail = parsed
            log(f"[{threadName}] Request: {method} {path} {version}")

            # Validate Host header
            hostHDR = headers.get("host")
            expectedHost = f"{HOST}:{PORT}"
            if not hostHDR:
                body = errorPage(400, "Bad Request", "Missing Host header.")
                hdr = buildHeaders(400, "Bad Request", contentLen=len(body.encode()))
                conn.sendall((hdr + body).encode())
                log(f"[{threadName}] Missing Host header -> 400")
                break
            if hostHDR not in [expectedHost, f"localhost:{PORT}", f"127.0.0.1:{PORT}"]:
                body = errorPage(403, "Forbidden", "Host header mismatch.")
                hdr = buildHeaders(403, "Forbidden", contentLen=len(body.encode()))
                conn.sendall((hdr + body).encode())
                log(f"[{threadName}] Host mismatch -> 403")
                break

            # Connection header
            connHDR = headers.get("connection", "").lower()
            if version == "HTTP/1.0":
                keepAlive = connHDR == "keep-alive"
            else:
                keepAlive = connHDR != "close"

            # ---------------- GET ----------------
            if method.upper() == "GET":
                target = safePathJoin(BASE, path)
                if not target:
                    body = errorPage(403, "Forbidden", "Access denied.")
                    hdr = buildHeaders(403, "Forbidden", contentLen=len(body.encode()))
                    conn.sendall((hdr + body).encode())
                    log(f"[{threadName}] Forbidden -> {path}")
                    continue
                if not os.path.exists(target) or not os.path.isfile(target):
                    body = errorPage(404, "Not Found", "Resource not found.")
                    hdr = buildHeaders(404, "Not Found", contentLen=len(body.encode()))
                    conn.sendall((hdr + body).encode())
                    log(f"[{threadName}] Not Found -> {path}")
                    continue

                ext = os.path.splitext(target)[1].lower()
                if ext in (".html", ".htm"):
                    with open(target, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read().encode()
                    headersExtra = [
                        f"Connection: {'keep-alive' if keepAlive else 'close'}",
                        f"Keep-Alive: timeout={KEEPALIVE_TIMEOUT}, max={REQ_LIMIT_PER_CONN}"
                    ]
                    hdr = buildHeaders(200, "OK", headers=headersExtra, contentLen=len(content), contentType="text/html; charset=utf-8")
                    conn.sendall(hdr.encode() + content)
                    log(f"[{threadName}] Served HTML {os.path.basename(target)}")
                elif ext in (".png", ".jpg", ".jpeg", ".txt"):
                    with open(target, "rb") as f:
                        content = f.read()
                    headersExtra = [
                        f"Content-Disposition: attachment; filename=\"{os.path.basename(target)}\"",
                        f"Connection: {'keep-alive' if keepAlive else 'close'}"
                    ]
                    hdr = buildHeaders(200, "OK", headers=headersExtra, contentLen=len(content), contentType="application/octet-stream")
                    conn.sendall(hdr.encode() + content)
                    log(f"[{threadName}] Served binary {os.path.basename(target)}")
                else:
                    body = errorPage(415, "Unsupported Media Type", "File type not supported.")
                    hdr = buildHeaders(415, "Unsupported Media Type", contentLen=len(body.encode()))
                    conn.sendall((hdr + body).encode())
                    log(f"[{threadName}] Unsupported type {ext}")

            # ---------------- POST ----------------
            elif method.upper() == "POST":
                ctype = headers.get("content-type", "")
                clen = int(headers.get("content-length", 0) or 0)
                if "application/json" not in ctype:
                    body = errorPage(415, "Unsupported Media Type", "Only JSON supported.")
                    hdr = buildHeaders(415, "Unsupported Media Type", contentLen=len(body.encode()))
                    conn.sendall((hdr + body).encode())
                    log(f"[{threadName}] Wrong Content-Type -> 415")
                    continue

                # Read full JSON body
                bodyBytes = bodyTail.encode() if bodyTail else b""
                toRead = clen - len(bodyBytes)
                while toRead > 0:
                    chunk = conn.recv(min(4096, toRead))
                    if not chunk:
                        break
                    bodyBytes += chunk
                    toRead -= len(chunk)

                try:
                    payload = json.loads(bodyBytes.decode())
                except Exception:
                    body = errorPage(400, "Bad Request", "Invalid JSON.")
                    hdr = buildHeaders(400, "Bad Request", contentLen=len(body.encode()))
                    conn.sendall((hdr + body).encode())
                    log(f"[{threadName}] Invalid JSON -> 400")
                    continue

                # Save file
                fname = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.json"
                fpath = os.path.join(UPLOADS, fname)
                with open(fpath, "w", encoding="utf-8") as wf:
                    json.dump(payload, wf, ensure_ascii=False, indent=2)

                respBody = json.dumps({
                    "status": "success",
                    "message": "File created successfully",
                    "filepath": f"/uploads/{fname}"
                })
                headersExtra = [f"Connection: {'keep-alive' if keepAlive else 'close'}"]
                hdr = buildHeaders(201, "Created", headers=headersExtra, contentLen=len(respBody.encode()), contentType="application/json")
                conn.sendall(hdr.encode() + respBody.encode())
                log(f"[{threadName}] POST saved {fpath}")

            else:
                body = errorPage(405, "Method Not Allowed", "Only GET and POST are supported.")
                hdr = buildHeaders(405, "Method Not Allowed", contentLen=len(body.encode()))
                conn.sendall((hdr + body).encode())
                log(f"[{threadName}] Unsupported method {method}")

            requestsServed += 1
            if not keepAlive:
                break

        except socket.timeout:
            log(f"[{threadName}] Connection timeout.")
            break
        except ConnectionResetError:
            log(f"[{threadName}] Connection reset by client.")
            break
        except Exception as e:
            log(f"[{threadName}] 500: {e}")
            try:
                body = errorPage(500, "Internal Server Error", str(e))
                hdr = buildHeaders(500, "Internal Server Error", contentLen=len(body.encode()))
                conn.sendall((hdr + body).encode())
            except:
                pass
            break

    # close connection AFTER loop
    try:
        conn.shutdown(socket.SHUT_RDWR)
    except:
        pass
    conn.close()
    log(f"[{threadName}] Connection closed (served {requestsServed} requests)")

# ------------------ Worker Thread ------------------ #
def worker(q):
    while True:
        conn, addr = q.get()
        try:
            handleConnection(conn, addr)
        finally:
            q.task_done()

# ------------------ Main Server ------------------ #
def main():
    q = Queue(maxsize=QUEUE_SIZE)
    for _ in range(MAX_THREADS):
        Thread(target=worker, args=(q,), daemon=True).start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(50)

    log(f"HTTP Server started on http://{HOST}:{PORT}")
    log(f"Thread pool size: {MAX_THREADS}")
    log(f"Serving from '{BASE}'")

    try:
        while True:
            conn, addr = sock.accept()
            try:
                q.put((conn, addr), block=True, timeout=5)
                log(f"Connection queued: {addr}")
            except Exception:
                body = errorPage(503, "Service Unavailable", "Server busy, try again later.")
                hdr = buildHeaders(503, "Service Unavailable", headers=["Retry-After: 5"], contentLen=len(body.encode()))
                try:
                    conn.sendall((hdr + body).encode())
                except:
                    pass
                conn.close()
                log(f"Queue full -> rejected {addr}")
    except KeyboardInterrupt:
        log("Shutdown requested, closing server.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
