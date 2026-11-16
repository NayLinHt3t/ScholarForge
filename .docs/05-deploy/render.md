# Hosting ScholarForge for $0 — no credit card (Render + Firestore Spark + Groq)

Nothing in this setup asks for a card, and nothing can charge you. When a free limit is reached, the service pauses instead of billing.

```
Browser ──https──> Render free web service (Singapore)  — FastAPI app + on-server search ranking
                       ├── Firestore, Spark plan     (users, projects, papers, notes, logs)
                       ├── Groq free API             (AI answers, summaries, outlines)
                       └── Semantic Scholar / OpenAlex (paper search)
```

| Part | Free limit | What happens at the limit |
|---|---|---|
| Render web service | 512 MB RAM, 750 hours/month; sleeps after 15 min without visitors, ~1 min to wake | service pauses until next month |
| Firestore (Spark) | 50,000 reads + 20,000 writes per day | database refuses requests until the daily reset (no charge) |
| Groq | about 30 requests/min, 1,000/day for `openai/gpt-oss-20b` | AI answers say "try again"; the rest of the app works |

Built into the app to stay inside these limits:
- The access log is written in **batches**: one database write per ~100 requests (or every 10 minutes).
- Logs older than 91 days are **deleted by the app itself**.
- If the ranking model can't run, **search still works**: it shows papers in the order the search libraries returned them.

---

## Step 1 — Push the code to GitHub

On your Mac, in the project folder:

```bash
cd ~/workspace/software-caseStudypj
git checkout ui-redesign-simple
git push --force-with-lease origin ui-redesign-simple
```

Render deploys from GitHub. If `NayLinHt3t/ScholarForge` is not your own GitHub account, ask its owner to add you, or fork it to your account.

## Step 2 — Get a free Groq key (no card)

1. Sign up at https://console.groq.com → **API Keys** → **Create API Key**. Copy it (starts with `gsk_`).
2. Optional test:
   ```bash
   curl -s https://api.groq.com/openai/v1/chat/completions \
     -H "Authorization: Bearer gsk_PASTE_KEY" -H "Content-Type: application/json" \
     -d '{"model":"openai/gpt-oss-20b","messages":[{"role":"user","content":"Say hi"}]}' | head -c 300; echo
   ```

## Step 3 — Make the admin password hash

```bash
source .venv/bin/activate
python -m app.tools.admin_password
```

Copy **only the hash** (the part starting `$2b$12$`, 60 characters, **without** the quotes).

## Step 4 — Create the Render web service

1. Go to https://render.com → **Get Started** → sign up with **GitHub** (no card).
2. **+ New** → **Web Service** → choose the `ScholarForge` repository (click *Configure GitHub* if it isn't listed).
3. Fill in:

| Field | Value |
|---|---|
| Name | `scholarforge` |
| Language | **Docker** (detected from the `Dockerfile`) |
| Branch | `ui-redesign-simple` |
| Region | **Singapore** |
| Instance Type | **Free** |

4. **Environment Variables** → add each (*Add Environment Variable*):

| Key | Value |
|---|---|
| `GOOGLE_CLOUD_PROJECT` | `scholarforge-84902` |
| `GOOGLE_APPLICATION_CREDENTIALS` | `/etc/secrets/serviceAccountKey.json` |
| `AI_PROVIDER` | `groq` |
| `GROQ_API_KEY` | your `gsk_…` key |
| `ADMIN_USERNAME` | `admin` (or your choice) |
| `ADMIN_PASSWORD_HASH` | the 60-character hash from step 3, **no quotes** |
| `DASHBOARD_TZ` | `Asia/Bangkok` |

5. **Secret Files** → *Add Secret File*:
   - Filename: `serviceAccountKey.json`
   - Contents: open `serviceAccountKey.json` from your project folder in a text editor, select all, copy, paste here.

   This is how the app logs in to Firestore. Never commit this file to GitHub (it's already in `.gitignore`).

6. **Advanced** → **Health Check Path**: `/auth/login`
7. Click **Deploy Web Service**. The first build takes about 5–10 minutes (it downloads the small search-ranking model into the image). Watch the **Logs** tab.

When it says **Live**, your URL is at the top: `https://scholarforge-xxxx.onrender.com`.

## Step 5 — Check it works

1. Open the URL → **Sign up** as a student → **Settings** → *AI assistant* says **Ready**.
2. Create a project → **Find papers** → save a paper → open it → **Ask about this paper**.
3. Open `https://scholarforge-xxxx.onrender.com/admin` → sign in with your admin username and password → **Usage dashboard**.
   - Activity shows up **within about 10 minutes**, because the log is written in batches.

## If something goes wrong

| You see | Fix |
|---|---|
| Logs show **"Out of memory"**, or the service restarts during a search | The ranking model doesn't fit in 512 MB. Add env var `EMBED_PROVIDER` = `none` → **Save, rebuild and deploy**. Search keeps working without smart ranking. |
| "The AI service isn't responding right now" | Groq free limit reached; wait a minute (or until tomorrow for the daily limit). Check the key in Environment. |
| Pages error with `PermissionDenied` / `403` in logs | The secret file is wrong or missing, or the filename isn't exactly `serviceAccountKey.json` |
| `Quota exceeded` / `RESOURCE_EXHAUSTED` in logs | Firestore's free daily limit is used up; it resets at midnight Pacific time (3 pm in Thailand) |
| Admin login: "Wrong username or password" | The hash in `ADMIN_PASSWORD_HASH` must be exactly 60 characters and have no quotes |
| First page load takes ~1 minute | Normal on the free plan: the service was asleep |

## Everyday use

| Task | How |
|---|---|
| Deploy new code | `git push` to `ui-redesign-simple` — Render redeploys automatically |
| Read logs | Render dashboard → your service → **Logs** |
| Check database usage | Firebase console → **Firestore Database** → **Usage** |
| Change admin password | make a new hash (step 3) → update `ADMIN_PASSWORD_HASH` in Render → **Save** |
| Take the site offline | Render → service → **Settings** → **Suspend** (or Delete) |

## Privacy (PDPA)

- AI answers, summaries and outlines send **paper abstracts and the questions students type** to Groq. Groq is reported not to train models on API data. Confirm in Groq's current terms (https://groq.com/terms-of-use) before launch.
- Search descriptions stay on the server (ranking runs inside the app).
- The Terms page (v1.1) names Groq automatically. **Existing accounts agreed to v1.0** ("no external AI service"), so ask them to accept the new terms before relying on the hosted version.
- `serviceAccountKey.json` gives full access to your Firebase project. Keep it only in Render's Secret Files and on your Mac.
