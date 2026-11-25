# BetplayExposed site — MANIFEST

Deployable version of the BetPlay complaint site. Staged at
`~/workspace/betplay-site/`. Nothing is deployed, bought, or created
anywhere else — this is code only, ready to push to GitHub and deploy.

One app serves every domain: no domain name is hardcoded in the app
code (verified by grep — `betplayistrash.fun` appears only in
`README.md` as the first domain to connect). Additional domains are a
hosting setting, not a code change (see README.md, "Add more domains").

## Files

| File | What it does |
|---|---|
| `app.py` | The whole backend. Flask app + SQLite posts table. Routes: `/` home, `/board` Victim Reports board, `GET /api/posts`, `POST /api/posts` (JSON or form), `GET /health`. `DB_PATH` env var sets the database location (default `data/posts.db`). No domain anywhere. |
| `templates/index.html` | Home page, matching the poster screenshot: BetplayExposed header + "INVESTIGATING. EXPOSING. PROTECTING." tagline, "BETPLAY IS CHEATING 100%" headline, the algorithm quote, "DEMAND IMMEDIATE SHUTDOWN OF THEIR SERVERS", the 777/BAR slot reel, the menu (Victim Reports is live, the rest marked "soon"), "THE SYSTEM IS RIGGED" footer, Mission Statement button (opens the popup), Join the Talks button (→ /board). The mission popup has its own Join the Talks button. |
| `templates/board.html` | Victim Reports board page: post form (display name optional, amount lost optional, story required), post list newest first, "No stories yet" empty state, back-to-home link. |
| `static/style.css` | All styling: black/red poster theme, distressed headline, CSS-built slot reel. Self-contained — no web fonts, no external requests. |
| `requirements.txt` | Flask 3.1.0, gunicorn 22.0.0. |
| `Procfile` | `web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60` |
| `runtime.txt` | python-3.12.3 |
| `.gitignore` | Ignores venv, `__pycache__`, `data/*.db*`, `.env`. |
| `README.md` | Full deploy steps: local run, Railway (recommended — persistent SQLite volume), Vercel caveat (serverless filesystem is ephemeral, needs an external DB first), how to connect betplayistrash.fun, and how to add more domains to the same deployment. |
| `MANIFEST.md` | This file. |

## Smoke test (2026-11-25, local, all passed)

- Fresh venv, `pip install -r requirements.txt` (Flask 3.1.0, gunicorn OK).
- Started with `DB_PATH=/tmp/betplay-test.db PORT=5001`.
- `GET /health` → `{"ok": true}`.
- `GET /` → home page contains (case-insensitive) BETPLAY / IS CHEATING
  / 100% / Mission Statement / Join the Talks / DEMAND IMMEDIATE
  SHUTDOWN / THE SYSTEM IS RIGGED / placed against, and the mission
  popup text "not affiliated with BetPlay".
- `GET /api/posts` → `[]` (board starts empty).
- `POST /api/posts` (test story, anonymous, $200) → 201, post id 1.
- `GET /api/posts` → the 1 test post; `GET /board` → story visible.
- Deleted the test row via sqlite3 → `GET /api/posts` → `[]`,
  board shows "No stories yet".
- Server stopped, test DB and venv removed. Shipped board is empty
  (0 posts). No victim stories were invented or seeded.

## Next steps to go live (for the parent agent)

1. Push `~/workspace/betplay-site/` to a GitHub repo.
2. Railway → New Project → Deploy from GitHub repo → pick it.
3. Add a Volume mounted at `/data`; set `DB_PATH=/data/posts.db`.
4. Railway service → Settings → Networking → Custom Domain → add
   `betplayistrash.fun`; add the CNAME it shows at the registrar
   (Vercel DNS) and wait for propagation.
5. Open `https://betplayistrash.fun`, check the poster home page, open
   the mission popup, tap Join the Talks, post a test story, confirm it
   shows, then delete that row from the database.
6. Later domains: same service, Custom Domain → add each one + its
   CNAME. No new project, repo, or code copy.
