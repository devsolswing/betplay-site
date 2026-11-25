"""BetPlay victim board — one small Flask app, one SQLite database.

Serves the BetplayExposed poster home page, the mission popup, and the
Victim Reports board where anyone can post a story anonymously.

No domain name is hardcoded anywhere in this app: it serves the same
site on whatever domain points at it, so one deployment can carry
several custom domains (see README.md).

Posts are stored server-side in SQLite so every visitor sees the same
board. Set DB_PATH to a persistent location in production (for example
/data/posts.db on a Railway volume).
"""

import os
import sqlite3
from datetime import date

from flask import Flask, Response, g, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["DB_PATH"] = os.environ.get("DB_PATH", os.path.join("data", "posts.db"))
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # 64 KB per post, plenty


def get_db():
    if "db" not in g:
        db_path = app.config["DB_PATH"]
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute(
            """CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL DEFAULT '',
                amount_lost TEXT NOT NULL DEFAULT '',
                story TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )"""
        )
        g.db.commit()
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def list_posts():
    rows = get_db().execute(
        "SELECT id, name, amount_lost, story, created_at FROM posts"
        " ORDER BY id DESC"
    ).fetchall()
    return [dict(r) for r in rows]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/board")
def board():
    posts = list_posts()
    return render_template("board.html", posts=posts)


@app.route("/api/posts", methods=["GET"])
def api_list_posts():
    return jsonify(list_posts())


@app.route("/api/posts", methods=["POST"])
def api_create_post():
    data = request.get_json(silent=True) or request.form
    story = (data.get("story") or "").strip()
    if not story:
        return jsonify({"error": "story is required"}), 400
    if len(story) > 5000:
        return jsonify({"error": "story is too long (max 5000 characters)"}), 400
    name = (data.get("name") or "").strip()[:80]
    amount = (data.get("amount_lost") or "").strip()[:40]
    db = get_db()
    cur = db.execute(
        "INSERT INTO posts (name, amount_lost, story) VALUES (?, ?, ?)",
        (name, amount, story),
    )
    db.commit()
    post = dict(
        db.execute(
            "SELECT id, name, amount_lost, story, created_at FROM posts WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()
    )
    if request.is_json:
        return jsonify(post), 201
    return redirect(url_for("board"))


@app.route("/health")
def health():
    return jsonify({"ok": True})


@app.route("/robots.txt")
def robots():
    body = "User-agent: *\nAllow: /\nSitemap: " + request.url_root + "sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    today = date.today().isoformat()
    urls = "".join(
        f"<url><loc>{request.url_root.rstrip('/')}{p}</loc>"
        f"<lastmod>{today}</lastmod><changefreq>daily</changefreq></url>"
        for p in ("/", "/board")
    )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + urls
        + "</urlset>"
    )
    return Response(body, mimetype="application/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
