# BetplayExposed — victim board site

One small Flask + SQLite app. Three things, nothing more:

1. **Home page** — the black/red BetplayExposed poster ("BETPLAY IS
   CHEATING 100%", slot reel 777 / BAR, menu, "THE SYSTEM IS RIGGED"
   footer).
2. **Mission Statement button** — opens a popup with the mission.
3. **Join the Talks button** — goes to the Victim Reports board, where
   anyone can post a story anonymously (optional name, optional amount
   lost). Posts are stored server-side in SQLite, newest first, so every
   visitor sees the same board. The board ships empty (0 posts).

## One app, many domains

**No domain name is hardcoded anywhere in this code.** The app serves
the same site and the same shared board on whatever domain points at
it. To run the site on more domains, do NOT copy the code — just add
each new domain to the same deployment (see "Add more domains" below).
One deployment, one board, every domain shows it.

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
# open http://127.0.0.1:5000
```

Posts are stored in `data/posts.db` by default. Override with:

```bash
DB_PATH=/data/posts.db .venv/bin/python app.py
```

## Deploy — recommended: Railway (posts persist)

Railway is the recommended host because the board needs a database
that survives redeploys, and Railway volumes do that. Vercel's
serverless filesystem does not (see "Vercel" below).

1. Push this folder to a GitHub repo (e.g. `devsolswing/betplay-site`).
2. Railway → **New Project → Deploy from GitHub repo** → pick the repo.
   Railway detects Python and installs `requirements.txt`; the
   `Procfile` starts gunicorn.
3. In the service, add a **Volume** with mount path `/data`.
4. Set the variable **`DB_PATH=/data/posts.db`**.
5. Railway gives the service a public domain like
   `betplay-site-production.up.railway.app`. Open it and check the home
   page loads and the board works.
6. **First custom domain — betplayistrash.fun:** in the Railway service
   go to **Settings → Networking → Custom Domain** and add
   `betplayistrash.fun`. Railway shows a DNS target (a CNAME value).
   At the registrar where the domain lives (Vercel): open the domain's
   **DNS records** and add a **CNAME** record, host `@`, pointing at
   the Railway target. Wait for DNS to propagate (usually minutes),
   then open `https://betplayistrash.fun` — the site should load with a
   valid certificate (Railway provisions it automatically).

## Add more domains (same site, same board)

Do not create another project, repo, or copy of the code. For each new
domain, repeat only step 6 above on the **same** Railway service:

1. Railway service → **Settings → Networking → Custom Domain** → add
   the new domain.
2. At the domain's registrar, add a **CNAME** record, host `@`,
   pointing at the same Railway target.
3. Open the new domain — it serves the identical site and the identical
   shared board. All domains read and write the same `posts.db`.

## Deploy — alternative: Vercel (needs an external database first)

Vercel can host the pages, but its serverless filesystem is ephemeral:
SQLite posts written on one request can disappear on the next
redeploy or instance recycle, so the shared board would not be
reliable. Do **not** deploy the board to Vercel as-is. If Vercel is
required, attach an external database first (e.g. Vercel Postgres or
Turso) and change `app.py` to use it instead of the local SQLite file.

If that is done, the multi-domain part on Vercel is the same idea:
one project, then **Project → Settings → Domains** and add each domain
(the first is `betplayistrash.fun`, the rest later). One project, one
deployment, every domain serves it.

## Routes

| Route | What it does |
|---|---|
| `GET /` | Poster home page (mission popup + Join the Talks) |
| `GET /board` | Victim Reports board + post form |
| `GET /api/posts` | JSON list of posts, newest first |
| `POST /api/posts` | Create a post (JSON or form: `story` required, `name` and `amount_lost` optional). JSON gets a `201` + the post; a form submit redirects to `/board`. |
| `GET /health` | `{"ok": true}` |

## Notes

- No victim stories are seeded. The board starts empty.
- Posts are public by design: anything typed is visible to everyone.
  There is no login, no moderation panel, and no delete button in the
  UI. To remove a post, delete its row from the database, e.g.:
  `sqlite3 /data/posts.db "DELETE FROM posts WHERE id = <id>;"`.
- Keep `DB_PATH` on a persistent volume in production. The default
  `data/posts.db` is fine for local runs only.
