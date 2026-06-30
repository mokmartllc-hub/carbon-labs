"""
Carbon Labs backend — stdlib only (no pip install required).
Run: py server.py
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import secrets
import sqlite3
import string
import time
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR.parent / "public"
DB_PATH = BASE_DIR / "carbon_labs.db"
SECRET_KEY = os.environ.get("CARBON_LABS_SECRET", "dev-change-me-in-production-carbon-labs-2026")
TOKEN_TTL_SECONDS = 30 * 24 * 3600
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# --- Database ---


def db_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with db_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                used INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS carts (
                user_id INTEGER PRIMARY KEY,
                items_json TEXT NOT NULL DEFAULT '[]',
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_number TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'pending',
                items_json TEXT NOT NULL,
                subtotal REAL NOT NULL,
                savings REAL NOT NULL DEFAULT 0,
                total REAL NOT NULL,
                shipping_name TEXT NOT NULL,
                shipping_email TEXT NOT NULL,
                shipping_phone TEXT,
                shipping_address TEXT NOT NULL,
                shipping_city TEXT NOT NULL,
                shipping_state TEXT NOT NULL,
                shipping_zip TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                order_number TEXT,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS newsletter_subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()


# --- Auth helpers ---


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt, digest = stored.split("$", 2)
        if scheme != "pbkdf2_sha256":
            return False
        check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
        return secrets.compare_digest(check.hex(), digest)
    except Exception:
        return False


def b64url(data: bytes) -> str:
    import base64

    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def b64url_decode(data: str) -> bytes:
    import base64

    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def sign_token(user_id: int, email: str) -> str:
    payload = json.dumps(
        {"sub": user_id, "email": email, "exp": int(time.time()) + TOKEN_TTL_SECONDS},
        separators=(",", ":"),
    )
    body = b64url(payload.encode())
    sig = hashlib.sha256((body + SECRET_KEY).encode()).hexdigest()
    return f"{body}.{sig}"


def verify_token(token: str) -> Optional[dict]:
    try:
        body, sig = token.rsplit(".", 1)
        expected = hashlib.sha256((body + SECRET_KEY).encode()).hexdigest()
        if not secrets.compare_digest(sig, expected):
            return None
        payload = json.loads(b64url_decode(body))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


def user_public(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "first": row["first_name"], "last": row["last_name"], "email": row["email"]}


def get_user_from_auth(header: Optional[str]) -> Optional[dict]:
    if not header or not header.startswith("Bearer "):
        return None
    payload = verify_token(header[7:].strip())
    if not payload:
        return None
    with db_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (payload["sub"],)).fetchone()
    return user_public(row) if row else None


def json_response(handler: BaseHTTPRequestHandler, status: int, data: Any) -> None:
    body = json.dumps(data).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", 0))
    raw = handler.rfile.read(length) if length else b"{}"
    return json.loads(raw.decode() or "{}")


def valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email.strip()))


def order_number() -> str:
    return "CL-" + "".join(random.choices(string.digits, k=5))


# --- API routes ---


def handle_api(handler: BaseHTTPRequestHandler, path: str, method: str) -> bool:
    auth = handler.headers.get("Authorization")
    user = get_user_from_auth(auth)

    if path == "/api/health" and method == "GET":
        json_response(handler, 200, {"status": "ok", "service": "carbon-labs"})
        return True

    if path == "/api/auth/register" and method == "POST":
        body = read_json(handler)
        first = (body.get("first") or "").strip()
        last = (body.get("last") or "").strip()
        email = (body.get("email") or "").strip().lower()
        password = body.get("password") or ""
        if not first or not last or not valid_email(email) or len(password) < 8:
            json_response(handler, 400, {"detail": "Invalid registration data"})
            return True
        with db_conn() as conn:
            if conn.execute("SELECT id FROM users WHERE lower(email)=?", (email,)).fetchone():
                json_response(handler, 400, {"detail": "An account with this email already exists"})
                return True
            cur = conn.execute(
                "INSERT INTO users (first_name, last_name, email, password_hash) VALUES (?,?,?,?)",
                (first, last, email, hash_password(password)),
            )
            uid = cur.lastrowid
            conn.execute("INSERT INTO carts (user_id, items_json) VALUES (?, '[]')", (uid,))
            row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
            conn.commit()
        u = user_public(row)
        json_response(handler, 200, {"token": sign_token(u["id"], u["email"]), "user": u})
        return True

    if path == "/api/auth/login" and method == "POST":
        body = read_json(handler)
        email = (body.get("email") or "").strip().lower()
        password = body.get("password") or ""
        with db_conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE lower(email)=?", (email,)).fetchone()
        if not row or not verify_password(password, row["password_hash"]):
            json_response(handler, 401, {"detail": "Incorrect email or password"})
            return True
        u = user_public(row)
        json_response(handler, 200, {"token": sign_token(u["id"], u["email"]), "user": u})
        return True

    if path == "/api/auth/me" and method == "GET":
        if not user:
            json_response(handler, 401, {"detail": "Not authenticated"})
            return True
        json_response(handler, 200, {"user": user})
        return True

    if path == "/api/auth/forgot-password" and method == "POST":
        body = read_json(handler)
        email = (body.get("email") or "").strip().lower()
        if valid_email(email):
            with db_conn() as conn:
                u = conn.execute("SELECT id FROM users WHERE lower(email)=?", (email,)).fetchone()
                if u:
                    token = secrets.token_urlsafe(32)
                    exp = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
                    conn.execute(
                        "INSERT INTO password_resets (user_id, token, expires_at) VALUES (?,?,?)",
                        (u["id"], token, exp),
                    )
                    conn.commit()
                    print(f"[Carbon Labs] Password reset for {email}: http://localhost:8000/?reset={token}")
        json_response(handler, 200, {"ok": True, "message": "If that email exists, a reset link has been sent."})
        return True

    if path == "/api/auth/reset-password" and method == "POST":
        body = read_json(handler)
        token = (body.get("token") or "").strip()
        password = body.get("password") or ""
        if len(password) < 8:
            json_response(handler, 400, {"detail": "Password must be at least 8 characters"})
            return True
        now = datetime.now(timezone.utc).isoformat()
        with db_conn() as conn:
            row = conn.execute(
                "SELECT * FROM password_resets WHERE token=? AND used=0 AND expires_at>?",
                (token, now),
            ).fetchone()
            if not row:
                json_response(handler, 400, {"detail": "Invalid or expired reset token"})
                return True
            conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(password), row["user_id"]))
            conn.execute("UPDATE password_resets SET used=1 WHERE id=?", (row["id"],))
            conn.commit()
        json_response(handler, 200, {"ok": True, "message": "Password updated. You can log in now."})
        return True

    if path == "/api/cart" and method == "GET":
        if not user:
            json_response(handler, 401, {"detail": "Not authenticated"})
            return True
        with db_conn() as conn:
            row = conn.execute("SELECT items_json FROM carts WHERE user_id=?", (user["id"],)).fetchone()
        items = json.loads(row["items_json"]) if row else []
        json_response(handler, 200, {"items": items})
        return True

    if path == "/api/cart" and method == "PUT":
        if not user:
            json_response(handler, 401, {"detail": "Not authenticated"})
            return True
        body = read_json(handler)
        items = body.get("items") or []
        with db_conn() as conn:
            conn.execute(
                """
                INSERT INTO carts (user_id, items_json, updated_at) VALUES (?, ?, datetime('now'))
                ON CONFLICT(user_id) DO UPDATE SET items_json=excluded.items_json, updated_at=datetime('now')
                """,
                (user["id"], json.dumps(items)),
            )
            conn.commit()
        json_response(handler, 200, {"items": items})
        return True

    if path == "/api/orders" and method == "POST":
        if not user:
            json_response(handler, 401, {"detail": "Not authenticated"})
            return True
        body = read_json(handler)
        items = body.get("items") or []
        if not items:
            json_response(handler, 400, {"detail": "Cart is empty"})
            return True
        num = order_number()
        with db_conn() as conn:
            conn.execute(
                """
                INSERT INTO orders (
                    user_id, order_number, status, items_json, subtotal, savings, total,
                    shipping_name, shipping_email, shipping_phone,
                    shipping_address, shipping_city, shipping_state, shipping_zip, notes
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    user["id"],
                    num,
                    "confirmed",
                    json.dumps(items),
                    float(body.get("subtotal") or 0),
                    float(body.get("savings") or 0),
                    float(body.get("total") or 0),
                    (body.get("shipping_name") or "").strip(),
                    (body.get("shipping_email") or "").strip().lower(),
                    (body.get("shipping_phone") or "").strip() or None,
                    (body.get("shipping_address") or "").strip(),
                    (body.get("shipping_city") or "").strip(),
                    (body.get("shipping_state") or "").strip(),
                    (body.get("shipping_zip") or "").strip(),
                    (body.get("notes") or "").strip() or None,
                ),
            )
            conn.execute("UPDATE carts SET items_json='[]', updated_at=datetime('now') WHERE user_id=?", (user["id"],))
            conn.commit()
        json_response(
            handler,
            200,
            {"ok": True, "order_number": num, "message": "Order placed successfully."},
        )
        return True

    if path == "/api/orders" and method == "GET":
        if not user:
            json_response(handler, 401, {"detail": "Not authenticated"})
            return True
        with db_conn() as conn:
            rows = conn.execute(
                """
                SELECT id, order_number, status, subtotal, savings, total, created_at
                FROM orders WHERE user_id=? ORDER BY created_at DESC
                """,
                (user["id"],),
            ).fetchall()
        json_response(
            handler,
            200,
            {
                "orders": [
                    {
                        "id": r["id"],
                        "order_number": r["order_number"],
                        "status": r["status"],
                        "subtotal": r["subtotal"],
                        "savings": r["savings"],
                        "total": r["total"],
                        "created_at": r["created_at"],
                    }
                    for r in rows
                ]
            },
        )
        return True

    if path.startswith("/api/orders/") and method == "GET":
        if not user:
            json_response(handler, 401, {"detail": "Not authenticated"})
            return True
        num = path.split("/")[-1]
        with db_conn() as conn:
            row = conn.execute(
                "SELECT * FROM orders WHERE order_number=? AND user_id=?",
                (num, user["id"]),
            ).fetchone()
        if not row:
            json_response(handler, 404, {"detail": "Order not found"})
            return True
        json_response(
            handler,
            200,
            {
                "order": {
                    "order_number": row["order_number"],
                    "status": row["status"],
                    "items": json.loads(row["items_json"]),
                    "subtotal": row["subtotal"],
                    "savings": row["savings"],
                    "total": row["total"],
                    "shipping": {
                        "name": row["shipping_name"],
                        "email": row["shipping_email"],
                        "phone": row["shipping_phone"],
                        "address": row["shipping_address"],
                        "city": row["shipping_city"],
                        "state": row["shipping_state"],
                        "zip": row["shipping_zip"],
                    },
                    "notes": row["notes"],
                    "created_at": row["created_at"],
                }
            },
        )
        return True

    if path == "/api/contact" and method == "POST":
        body = read_json(handler)
        name = (body.get("name") or "").strip()
        email = (body.get("email") or "").strip().lower()
        subject = (body.get("subject") or "").strip()
        message = (body.get("message") or "").strip()
        if not name or not valid_email(email) or not subject or len(message) < 5:
            json_response(handler, 400, {"detail": "Invalid contact form data"})
            return True
        with db_conn() as conn:
            conn.execute(
                "INSERT INTO contact_messages (name, email, order_number, subject, message) VALUES (?,?,?,?,?)",
                (name, email, (body.get("order_number") or "").strip() or None, subject, message),
            )
            conn.commit()
        json_response(handler, 200, {"ok": True, "message": "Message received."})
        return True

    if path == "/api/newsletter" and method == "POST":
        body = read_json(handler)
        email = (body.get("email") or "").strip().lower()
        if not valid_email(email):
            json_response(handler, 400, {"detail": "Invalid email"})
            return True
        with db_conn() as conn:
            try:
                conn.execute("INSERT INTO newsletter_subscribers (email) VALUES (?)", (email,))
                conn.commit()
            except sqlite3.IntegrityError:
                pass
        json_response(handler, 200, {"ok": True, "message": "Subscribed."})
        return True

    return False


# --- Static files ---


MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}


class CarbonHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self) -> None:
        self._route("GET")

    def do_POST(self) -> None:
        self._route("POST")

    def do_PUT(self) -> None:
        self._route("PUT")

    def _route(self, method: str) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/api" or path.startswith("/api/"):
            if handle_api(self, path, method):
                return
            json_response(self, 404, {"detail": "Not found"})
            return

        if method != "GET":
            json_response(self, 405, {"detail": "Method not allowed"})
            return

        rel = path[1:] if path != "/" else "index.html"
        file_path = (PUBLIC_DIR / rel).resolve()
        if not str(file_path).startswith(str(PUBLIC_DIR.resolve())):
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if file_path.is_dir():
            file_path = file_path / "index.html"
        if not file_path.exists():
            file_path = PUBLIC_DIR / "index.html"

        data = file_path.read_bytes()
        ext = file_path.suffix.lower()
        self.send_response(200)
        self.send_header("Content-Type", MIME.get(ext, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    init_db()
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), CarbonHandler)
    print(f"Carbon Labs running at http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
