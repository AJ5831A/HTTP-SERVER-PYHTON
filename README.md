# Multi-threaded HTTP Server

A robust, production-ready HTTP/1.1 server implementation from scratch using Python socket programming with concurrent request handling, binary file transfer support, and comprehensive security features.

## 🚀 Features

- **Multi-threaded Architecture**: Thread pool with configurable size for handling concurrent connections
- **HTTP/1.1 Compliance**: Full support for persistent connections (Keep-Alive)
- **Binary File Transfer**: Efficient streaming of images (PNG, JPEG) and text files
- **JSON API**: POST endpoint for JSON data processing and file uploads
- **Security Hardened**: Path traversal protection and Host header validation
- **Connection Management**: Automatic timeout handling and request limits
- **Comprehensive Logging**: Detailed request/response logging with timestamps

---

## 📋 Requirements

- Python 3.7 or higher
- No external dependencies (uses only Python standard library)

---

## 🏗️ Project Structure

```
project/
├── server.py                    # Main server implementation
├── README.md                    # This file
└── resources/                   # Static files directory
    ├── index.html               # Default homepage
    ├── about.html               # About page
    ├── contact.html             # Contact page
    ├── sample1.txt              # Sample text file
    ├── sample2.txt              # Another text file
    ├── LOGO.png                 # PNG image file
    ├── groupPhoto.jpeg          # JPEG image file
    └── uploads/                 # Directory for POST uploads (auto-created)
```

---

## 🔧 Installation & Setup

### 1. Clone the Repository

### 2. Verify Directory Structure

The `resources/` and `resources/uploads/` directories are automatically created when the server starts.

### 3. Add Test Files

Create sample HTML files in `resources/`:

**resources/index.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Multi-threaded HTTP Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        a { color: #0066cc; text-decoration: none; margin: 10px; display: inline-block; }
        a:hover { text-decoration: underline; }
        ul { line-height: 2; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Multi-threaded HTTP Server</h1>
        <p>This is a custom HTTP server built from scratch using Python sockets.</p>
        <nav>
            <a href="/about.html">About</a>
            <a href="/contact.html">Contact</a>
        </nav>
        <h2>Download Test Files:</h2>
        <ul>
            <li><a href="/LOGO.png">Download Logo (PNG)</a></li>
            <li><a href="/groupPhoto.jpeg">Download Group Photo (JPEG)</a></li>
            <li><a href="/sample1.txt">Download Sample Text 1</a></li>
            <li><a href="/sample2.txt">Download Sample Text 2</a></li>
        </ul>
    </div>
</body>
</html>
```

**resources/about.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>About - HTTP Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; }
        h1 { color: #333; }
        a { color: #0066cc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>About This Server</h1>
        <p>This HTTP server demonstrates:</p>
        <ul>
            <li>Multi-threaded concurrent request handling</li>
            <li>Binary file transfer (images, documents)</li>
            <li>JSON POST request processing</li>
            <li>Security features (path traversal protection)</li>
            <li>HTTP/1.1 persistent connections</li>
        </ul>
        <p><a href="/">← Back to Home</a></p>
    </div>
</body>
</html>
```

**resources/contact.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Contact - HTTP Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; }
        h1 { color: #333; }
        a { color: #0066cc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Contact</h1>
        <p>This is a demonstration HTTP server project.</p>
        <p>Built with Python socket programming.</p>
        <p><a href="/">← Back to Home</a></p>
    </div>
</body>
</html>
```

Add images and text files to the `resources/` directory for testing.

---

## 🚀 Running the Server

### Default Configuration (localhost:8080)

```bash
python3 server.py
```

### Custom Port

```bash
python3 server.py 8000
```

### Custom Host and Port

```bash
python3 server.py 8000 0.0.0.0
```

### Full Configuration (Port, Host, Thread Pool Size)

```bash
python3 server.py 8000 0.0.0.0 20
```

**Parameters:**
- **Argument 1**: Port number (default: 8080)
- **Argument 2**: Host address (default: 127.0.0.1)
- **Argument 3**: Maximum thread pool size (default: 10)

**Example Output:**
```
[2024-10-09 14:30:00] : HTTP Server started on http://127.0.0.1:8080
[2024-10-09 14:30:00] : Thread pool size: 10
[2024-10-09 14:30:00] : Serving from '/path/to/resources'
```

---

## 🧪 Testing the Server

### Using Web Browser

1. Start the server:
   ```bash
   python3 server.py
   ```

2. Open your browser and navigate to:
   - `http://localhost:8080/` - Homepage
   - `http://localhost:8080/about.html` - About page
   - `http://localhost:8080/contact.html` - Contact page
   - `http://localhost:8080/LOGO.png` - Downloads PNG file
   - `http://localhost:8080/groupPhoto.jpeg` - Downloads JPEG file
   - `http://localhost:8080/sample1.txt` - Downloads text file

### Using cURL

#### 1. GET Request (HTML)
```bash
# Get homepage
curl -v http://localhost:8080/

# Get specific HTML page
curl -v http://localhost:8080/about.html
```

#### 2. GET Request (Binary Download)
```bash
# Download PNG image
curl -v http://localhost:8080/LOGO.png -o downloaded_logo.png

# Download JPEG image
curl -v http://localhost:8080/groupPhoto.jpeg -o downloaded_photo.jpeg

# Download text file
curl -v http://localhost:8080/sample1.txt -o downloaded_sample.txt
```

#### 3. Verify File Integrity
```bash
# Compare checksums (Linux/Mac)
md5sum resources/LOGO.png downloaded_logo.png
sha256sum resources/LOGO.png downloaded_logo.png

# Windows PowerShell
Get-FileHash resources/LOGO.png
Get-FileHash downloaded_logo.png
```

#### 4. POST Request (JSON Upload)
```bash
curl -X POST http://localhost:8080/upload \
  -H "Content-Type: application/json" \
  -H "Host: localhost:8080" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Test message from curl"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "File created successfully",
  "filepath": "/uploads/upload_20241009_143022_a7b9c4.json"
}
```

#### 5. Testing Keep-Alive Connections
```bash
# Multiple requests on same connection
curl -v --keepalive-time 60 \
  http://localhost:8080/ \
  http://localhost:8080/about.html \
  http://localhost:8080/contact.html
```

#### 6. Security Tests

**Test Path Traversal Protection:**
```bash
# Should return 403 Forbidden
curl -v http://localhost:8080/../etc/passwd
curl -v http://localhost:8080/../../sensitive.txt
curl -v http://localhost:8080/.././../config
```

**Test Host Header Validation:**
```bash
# Should return 403 Forbidden
curl -v http://localhost:8080/ -H "Host: evil.com"

# Should return 400 Bad Request (no Host header)
curl -v http://localhost:8080/ -H "Host:"
```

**Test Unsupported Methods:**
```bash
# Should return 405 Method Not Allowed
curl -X PUT http://localhost:8080/index.html
curl -X DELETE http://localhost:8080/index.html
curl -X PATCH http://localhost:8080/index.html
```

**Test Wrong Content-Type for POST:**
```bash
# Should return 415 Unsupported Media Type
curl -X POST http://localhost:8080/upload \
  -H "Content-Type: text/plain" \
  -d "This is not JSON"
```

#### 7. Concurrent Connection Testing

**Using Apache Bench (ab):**
```bash
# Install apache2-utils first (Linux)
sudo apt-get install apache2-utils

# Test with 10 concurrent connections, 100 total requests
ab -n 100 -c 10 http://localhost:8080/
```

**Using Python script:**
```python
import requests
from concurrent.futures import ThreadPoolExecutor

def make_request(i):
    response = requests.get('http://localhost:8080/')
    print(f"Request {i}: Status {response.status_code}")

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(make_request, range(50))
```

---

## 🏛️ Architecture

### Thread Pool Implementation

The server uses a **fixed-size thread pool** with a connection queue:

```
┌─────────────────────────────────────────┐
│         Main Server Thread              │
│    (Accepts incoming connections)       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Connection Queue                │
│  (Queue size: 100, timeout: 5s)         │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┬──────────────┐
        ▼             ▼              ▼
   ┌────────┐   ┌────────┐     ┌────────┐
   │Thread 1│   │Thread 2│ ... │Thread N│
   │ Worker │   │ Worker │     │ Worker │
   └────────┘   └────────┘     └────────┘
```

**Key Features:**
- **Configurable pool size** (default: 10 threads)
- **Connection queuing** when all threads are busy
- **Automatic rejection** with 503 status when queue is full
- **Daemon threads** for clean shutdown

### Binary File Transfer

Binary files are transferred using a **streaming approach**:

1. **File is opened in binary mode** (`rb`)
2. **Entire file content is read** into memory
3. **Proper headers are set**:
   - `Content-Type: application/octet-stream`
   - `Content-Disposition: attachment; filename="..."`
   - `Content-Length: [bytes]`
4. **Data is sent via socket** using `conn.sendall()`

**Supported File Types:**
- `.txt` → Binary download
- `.png` → Binary download
- `.jpg`, `.jpeg` → Binary download
- `.html`, `.htm` → Rendered in browser

### Connection Management

**Keep-Alive Behavior:**
- HTTP/1.1: Persistent by default (unless `Connection: close`)
- HTTP/1.0: Non-persistent by default (unless `Connection: keep-alive`)
- **Timeout**: 30 seconds of inactivity
- **Max Requests**: 100 requests per connection
- **Proper closure**: `shutdown()` + `close()` on socket

---

## 🔒 Security Features

### 1. Path Traversal Protection

The `safePathJoin()` function prevents directory traversal attacks:

```python
def safePathJoin(base, reqPath):
    """Safely join request path with base directory"""
    target = os.path.abspath(os.path.join(base, reqPath))
    baseAbs = os.path.abspath(base)
    
    # Ensure target is within base directory
    if not target.startswith(baseAbs + os.sep):
        return None  # Forbidden
    
    return target
```

**Blocked Patterns:**
- `/../etc/passwd`
- `/../../sensitive.txt`
- `/.././../config`
- Absolute paths outside resources directory

### 2. Host Header Validation

Every request must include a valid `Host` header:

```python
# Accepted values
- localhost:8080
- 127.0.0.1:8080
- <configured-host>:<configured-port>

# Rejected
- Missing Host header → 400 Bad Request
- Mismatched Host header → 403 Forbidden
```

### 3. Input Validation

- Request size limited to 8192 bytes for headers
- JSON validation for POST requests
- File extension validation for GET requests
- Proper encoding handling with error replacement

### 4. Error Handling

- **Graceful degradation**: Errors don't crash the server
- **Proper status codes**: 400, 403, 404, 405, 415, 500, 503
- **Informative error pages**: HTML error responses
- **Logging**: All security violations are logged

---

## 📊 HTTP Status Codes

| Code | Status | Usage |
|------|--------|-------|
| 200 | OK | Successful GET request |
| 201 | Created | Successful POST request |
| 400 | Bad Request | Malformed request, missing Host, invalid JSON |
| 403 | Forbidden | Path traversal attempt, Host mismatch |
| 404 | Not Found | Resource doesn't exist |
| 405 | Method Not Allowed | Non-GET/POST methods (PUT, DELETE, etc.) |
| 415 | Unsupported Media Type | Wrong Content-Type or unsupported file extension |
| 500 | Internal Server Error | Server-side exceptions |
| 503 | Service Unavailable | Thread pool exhausted, queue full |

---

## 📝 Logging

The server provides comprehensive logging with timestamps:

### Server Startup
```
[2024-10-09 14:30:00] : HTTP Server started on http://127.0.0.1:8080
[2024-10-09 14:30:00] : Thread pool size: 10
[2024-10-09 14:30:00] : Serving from '/path/to/resources'
```

### Request Handling
```
[2024-10-09 14:30:15] : [Thread-54321] Connection from 127.0.0.1:54321
[2024-10-09 14:30:15] : [Thread-54321] Request: GET /LOGO.png HTTP/1.1
[2024-10-09 14:30:15] : [Thread-54321] Served binary LOGO.png
[2024-10-09 14:30:15] : [Thread-54321] Connection closed (served 1 requests)
```

### POST Requests
```
[2024-10-09 14:35:20] : [Thread-54400] Request: POST /upload HTTP/1.1
[2024-10-09 14:35:20] : [Thread-54400] POST saved /path/to/resources/uploads/upload_20241009_143520_abc123.json
```

### Security Events
```
[2024-10-09 14:40:10] : [Thread-54500] Forbidden -> /../etc/passwd
[2024-10-09 14:40:15] : [Thread-54501] Host mismatch -> 403
[2024-10-09 14:40:20] : [Thread-54502] Missing Host header -> 400
```

### Connection Queue
```
[2024-10-09 14:45:00] : Connection queued: ('127.0.0.1', 54600)
[2024-10-09 14:45:05] : Queue full -> rejected ('127.0.0.1', 54601)
```

---

## ⚠️ Known Limitations

1. **Memory Usage**: Large files are loaded entirely into memory before sending
   - **Impact**: May cause memory issues with files > 100MB
   - **Workaround**: Implement chunked transfer encoding for streaming

2. **Request Size**: Headers limited to 8192 bytes
   - **Impact**: Large cookie headers may be truncated
   - **Workaround**: Increase buffer size if needed

3. **Single Process**: Uses threading, not multiprocessing
   - **Impact**: Python GIL may limit CPU-bound operations
   - **Workaround**: Use multiprocessing or async I/O for CPU-intensive tasks

4. **No HTTPS**: Plain HTTP only, no TLS/SSL support
   - **Impact**: Data transmitted in cleartext
   - **Workaround**: Use reverse proxy (nginx) with SSL termination

5. **Static File Serving Only**: No dynamic content generation (CGI, PHP, etc.)
   - **Impact**: Cannot execute server-side scripts
   - **Workaround**: Extend with template engine or CGI support

6. **No Compression**: No gzip or deflate encoding
   - **Impact**: Larger transfer sizes for text files
   - **Workaround**: Add compression middleware

---

## 🔧 Configuration Options

Edit the constants at the top of `server.py`:

```python
PORT = 8080                    # Default port
HOST = "127.0.0.1"             # Default host
MAX_THREADS = 10               # Thread pool size
REQ_LIMIT_PER_CONN = 100       # Max requests per connection
QUEUE_SIZE = 100               # Connection queue size
KEEPALIVE_TIMEOUT = 30         # Seconds before connection timeout
```

---

## 🐛 Troubleshooting

### Problem: "Address already in use"
```bash
# Solution 1: Kill existing process
lsof -ti:8080 | xargs kill -9

# Solution 2: Use different port
python3 server.py 8081
```

### Problem: "Permission denied"
```bash
# Ports < 1024 require root on Linux/Mac
sudo python3 server.py 80

# Or use port >= 1024
python3 server.py 8080
```

### Problem: Files not downloading
- Ensure files exist in `resources/` directory
- Check file permissions (must be readable)
- Verify file extensions are supported (.png, .jpg, .jpeg, .txt)

### Problem: JSON POST failing
- Verify `Content-Type: application/json` header is set
- Ensure JSON is valid (use online validator)
- Check `Content-Length` header is correct

---

## 📚 References

- [RFC 7230 - HTTP/1.1 Message Syntax and Routing](https://tools.ietf.org/html/rfc7230)
- [RFC 7231 - HTTP/1.1 Semantics and Content](https://tools.ietf.org/html/rfc7231)
- [Python Socket Programming](https://docs.python.org/3/library/socket.html)
- [Python Threading](https://docs.python.org/3/library/threading.html)

---

## 👨‍💻 Author

Aryan Jakhar
[aryan.24bcs10305@sst.scaler.com]  

---

## 📄 License

This project is created for educational purposes as part of a networking assignment.

---

## 🎯 Assignment Checklist

- [x] Multi-threaded server with thread pool
- [x] TCP socket implementation
- [x] HTTP request parsing (GET, POST)
- [x] HTML file serving
- [x] Binary file transfer (PNG, JPEG, TXT)
- [x] JSON POST processing
- [x] Path traversal protection
- [x] Host header validation
- [x] Keep-Alive connection support
- [x] Proper HTTP response formatting
- [x] Comprehensive logging
- [x] Error handling (400, 403, 404, 405, 415, 500, 503)
- [x] Thread-safe operations
- [x] Connection timeout handling
- [x] Request limit per connection