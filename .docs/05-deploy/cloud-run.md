# Hosting ScholarForge for free (Google Cloud Run + Groq)

Everything below runs inside free tiers. Expected cost for a class-sized app: **$0/month**, or a few cents if usage spikes.

```
Browser ──https──> Cloud Run, Bangkok region (FastAPI app + on-server search embeddings)
                       ├── Firestore            (users, projects, papers, notes, logs)   free quota
                       ├── Groq API             (AI answers, summaries, outlines)        free tier
                       └── Semantic Scholar / OpenAlex (paper search)                    free
```

| Part | Free allowance | What uses it |
|---|---|---|
| Cloud Run | 2M requests, 180,000 vCPU-seconds, 360,000 GiB-seconds per month | every page load (only while a request is being handled) |
| Firestore | 50,000 reads, 20,000 writes per day, 1 GiB stored | app data + one access-log write per request |
| Groq (`openai/gpt-oss-20b`) | about 30 requests/minute and 1,000 requests/day (check your own limits page) | each AI answer, summary or outline = 1 request. **Search uses no Groq requests.** |
| Cloud Build | 2,500 build-minutes per month | each deploy (~3–5 minutes) |
| Artifact Registry | 0.5 GB stored | the app image; the cleanup rule in step 9 keeps only the newest |
| Secret Manager | 6 secret versions | the Groq key + admin password hash |

> **A card is still needed.** Google requires a billing account to use Cloud Run, even when you stay inside the free tier. Step 3 adds a budget alert so you get an email long before any real charge.

Run every command in **Terminal on your Mac**, inside the project folder, on the `ui-redesign-simple` branch.

---

## 1. Get a free Groq API key (no card needed)

1. Sign up at https://console.groq.com → **API Keys** → **Create API Key**. Copy it (starts with `gsk_`).
2. Test it:

```bash
export GROQ_API_KEY=gsk_xxx
curl -s https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"openai/gpt-oss-20b","messages":[{"role":"user","content":"Say hi"}]}' | head -c 300; echo
```

You should see `"content":"Hi…"`. Your exact free limits are at https://console.groq.com/settings/limits.

## 2. Install and log in to Google Cloud

```bash
brew install --cask google-cloud-sdk      # skip if `gcloud --version` already works
gcloud auth login
gcloud config set project scholarforge-84902
gcloud config set run/region asia-southeast3     # Bangkok — closest, and in the cheapest price tier
```

## 3. Turn on billing + a $1 budget alert (one time)

1. Firebase console → project **scholarforge-84902** → **Upgrade** → **Blaze**. Link or create a billing account.
2. Google Cloud console → **Billing** → **Budgets & alerts** → **Create budget**:
   - Projects: `scholarforge-84902`
   - Amount: **1 USD**
   - Alerts at 50%, 90% and 100% → emails to you.

A budget only *warns* you; it doesn't switch anything off. If you ever get an alert, look at **Billing → Reports** to see which service is using money.

## 4. Turn on the needed services (one time)

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com firestore.googleapis.com
```

## 5. Store the secrets (one time)

```bash
# Groq key
printf "%s" "$GROQ_API_KEY" | gcloud secrets create groq-api-key --data-file=-

# Admin password hash — type your admin password twice, then copy the hash it prints
python -m app.tools.admin_password
printf '%s' 'PASTE_THE_HASH_HERE' | gcloud secrets create admin-password-hash --data-file=-
```

Check the hash really is 60 characters: `gcloud secrets versions access latest --secret=admin-password-hash | wc -c` should print `60`.

## 6. Give the app its own identity (one time)

```bash
gcloud iam service-accounts create scholarforge-run --display-name="ScholarForge Cloud Run"
SA=scholarforge-run@scholarforge-84902.iam.gserviceaccount.com

gcloud projects add-iam-policy-binding scholarforge-84902 \
  --member="serviceAccount:$SA" --role="roles/datastore.user"
for s in groq-api-key admin-password-hash; do
  gcloud secrets add-iam-policy-binding $s --member="serviceAccount:$SA" --role="roles/secretmanager.secretAccessor"
done
```

On Cloud Run the app reaches Firestore as this identity. `serviceAccountKey.json` is **not** uploaded.

## 7. Auto-delete old logs and admin sessions (one time)

```bash
gcloud firestore fields ttls update expire_at --collection-group=access_log --enable-ttl
gcloud firestore fields ttls update expire_at --collection-group=admin_sessions --enable-ttl
```

Access-log entries are deleted after 91 days (Computer Crime Act §26 needs at least 90). These automatic deletes are not in Firestore's free quota, but they cost fractions of a cent.

## 8. Deploy

```bash
gcloud run deploy scholarforge \
  --source . \
  --service-account scholarforge-run@scholarforge-84902.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --memory 1Gi --cpu 1 \
  --min-instances 0 --max-instances 2 --concurrency 20 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=scholarforge-84902,AI_PROVIDER=groq,ADMIN_USERNAME=admin,DASHBOARD_TZ=Asia/Bangkok \
  --set-secrets GROQ_API_KEY=groq-api-key:latest,ADMIN_PASSWORD_HASH=admin-password-hash:latest
```

- If it asks to create an Artifact Registry repository, answer **Y**.
- The first build takes ~5 minutes (it downloads the search-embedding model into the image).
- `--min-instances 0` is what keeps it free: the app sleeps when nobody uses it. The first visit after a quiet period takes a few extra seconds to wake up.
- `--max-instances 2` caps how much it can ever scale up (and cost).

At the end it prints your URL: `https://scholarforge-….asia-southeast3.run.app`.

## 9. Keep only the newest image (one time, after the first deploy)

Each deploy stores a new image. This rule deletes old ones so storage stays inside the free 0.5 GB:

```bash
cat > /tmp/cleanup.json <<'JSON'
[
  {"name": "keep-newest", "action": {"type": "Keep"}, "mostRecentVersions": {"keepCount": 1}},
  {"name": "delete-old",  "action": {"type": "Delete"}, "condition": {"tagState": "any", "olderThan": "1d"}}
]
JSON
gcloud artifacts repositories set-cleanup-policies cloud-run-source-deploy \
  --location=asia-southeast3 --policy=/tmp/cleanup.json --no-dry-run
```

## 10. Check it works

1. Open the URL → **Sign up** as a student → **Settings** → *AI assistant* says **Ready**.
2. Create a project → **Find papers** → save a paper → open it → ask a question.
3. Open `https://…run.app/admin` → sign in as `admin` → your activity from step 2 is on the dashboard.

## Everyday commands

| Task | Command |
|---|---|
| Deploy a new version | run the step 8 command again |
| Read server logs | `gcloud run services logs read scholarforge --limit 100` |
| New admin password | `python -m app.tools.admin_password`, then `printf '%s' 'HASH' \| gcloud secrets versions add admin-password-hash --data-file=-`, then redeploy |
| New Groq key | `printf "%s" "gsk_new" \| gcloud secrets versions add groq-api-key --data-file=-`, then redeploy |
| Use another Groq model | add `,GROQ_MODEL=model-id` to `--set-env-vars` and redeploy |
| Take the site offline | `gcloud run services delete scholarforge` |

## Troubleshooting

| You see | Likely cause |
|---|---|
| "The AI service isn't responding right now" | Groq free limit reached (logs show `groq.chat.error status=429`): wait a minute, or until the next day for the daily limit |
| Search shows no AI ranking / errors right after deploy | look for `local_embed.load_failed` in the logs; rebuild with step 8 |
| 403 / PermissionDenied in logs | step 6 roles missing |
| Admin login says "isn't set up yet" | a secret is missing from the step 8 command |
| Signed out after every click | open the **https** URL (cookies are secure-only when hosted) |

## Privacy (PDPA)

- AI answers, summaries and outlines send **paper abstracts and the questions students type** to Groq. Groq's terms say it does not use this data to train models.
- **Search descriptions stay on the server.** Matching papers to a search runs on the server itself.
- The Terms page (v1.1) names Groq automatically. **Existing accounts agreed to v1.0** ("no external AI service"), so ask them to accept the new terms before relying on the hosted version.

## Paid alternative

To use Hugging Face Inference Providers instead of Groq, deploy with `AI_PROVIDER=huggingface,EMBED_PROVIDER=local` and an `HF_TOKEN` secret. Hugging Face needs purchased credits or a PRO plan.
