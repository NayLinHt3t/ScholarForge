# Hosting ScholarForge on Google Cloud Run

ScholarForge already stores its data in Firestore (project `scholarforge-84902`), so it is hosted on **Google Cloud Run** in the same project. AI runs on **Hugging Face Inference Providers**.

```
Student's browser ──https──> Cloud Run (FastAPI app, Singapore)
                                 ├── Firestore            (users, projects, papers, notes, access_log)
                                 ├── Hugging Face router  (chat + embeddings)
                                 └── Semantic Scholar / OpenAlex (paper search)
```

Run every command below in **Terminal on your Mac**, inside the project folder.

---

## 0. Before you start

| You need | Why |
|---|---|
| Google Cloud SDK (`gcloud`) | to deploy. Install: `brew install --cask google-cloud-sdk` |
| **Billing enabled** on `scholarforge-84902` (Firebase "Blaze" plan) | Cloud Run and Cloud Build need it. Small apps usually stay inside the free tier. |
| A Hugging Face account **with credits** | Free HF accounts get no included inference credits. Either buy credits or use the PRO plan (it includes $2/month). |

## 1. Create a Hugging Face token

1. Open https://huggingface.co/settings/tokens → **Create new token** → **Fine-grained**.
2. Tick **"Make calls to Inference Providers"**. Nothing else is needed.
3. Copy the token (starts with `hf_`).

Check that the token and both models work (paste your token in place of `hf_xxx`):

```bash
export HF_TOKEN=hf_xxx

# chat model
curl -s https://router.huggingface.co/v1/chat/completions \
  -H "Authorization: Bearer $HF_TOKEN" -H "Content-Type: application/json" \
  -d '{"model":"openai/gpt-oss-20b","messages":[{"role":"user","content":"Say hi"}]}' | head -c 400; echo

# embedding model
curl -s https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction \
  -H "Authorization: Bearer $HF_TOKEN" -H "Content-Type: application/json" \
  -d '{"inputs":["hello world"]}' | head -c 200; echo
```

You should see a reply with `"content"` and a list of numbers. If a model returns an error, pick another one on huggingface.co (the model page shows an **Inference Providers** box when it can be used). Then set `HF_CHAT_MODEL` / `HF_EMBED_MODEL` in step 6.

## 2. Log in to Google Cloud

```bash
gcloud auth login
gcloud config set project scholarforge-84902
gcloud config set run/region asia-southeast1      # Singapore — closest to Thailand
```

## 3. Turn on the needed services (one time)

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com firestore.googleapis.com
```

## 4. Store the Hugging Face token as a secret (one time)

The token is never put in code or in the container image.

```bash
printf "%s" "$HF_TOKEN" | gcloud secrets create hf-token --data-file=-
```

(To change it later: `printf "%s" "hf_new" | gcloud secrets versions add hf-token --data-file=-`)

## 5. Create the app's identity and give it only what it needs (one time)

```bash
gcloud iam service-accounts create scholarforge-run --display-name="ScholarForge Cloud Run"

SA=scholarforge-run@scholarforge-84902.iam.gserviceaccount.com

# read/write Firestore
gcloud projects add-iam-policy-binding scholarforge-84902 \
  --member="serviceAccount:$SA" --role="roles/datastore.user"

# read the HF token secret
gcloud secrets add-iam-policy-binding hf-token \
  --member="serviceAccount:$SA" --role="roles/secretmanager.secretAccessor"
```

On Cloud Run the app logs in to Firestore as this service account. You do **not** upload `serviceAccountKey.json` (it is excluded from the image).

## 6. Create the admin login (one time)

The admin portal (`/admin`) has its own username and password, separate from student accounts. Only a bcrypt **hash** of the password is stored — never the password itself.

```bash
python -m app.tools.admin_password          # type your admin password twice (min 12 characters)
```

It prints a hash. Store it as a secret (paste the hash in place of `HASH`):

```bash
printf '%s' 'HASH' | gcloud secrets create admin-password-hash --data-file=-
gcloud secrets add-iam-policy-binding admin-password-hash \
  --member="serviceAccount:$SA" --role="roles/secretmanager.secretAccessor"
```

## 6b. Make access-log entries and admin sessions delete themselves (one time)

Each log entry has an `expire_at` date. This tells Firestore to delete entries once that date passes, so the log is kept for the 90 days the Computer Crime Act §26 requires, and no longer.

```bash
gcloud firestore fields ttls update expire_at --collection-group=access_log --enable-ttl
gcloud firestore fields ttls update expire_at --collection-group=admin_sessions --enable-ttl
```

## 7. Deploy

Choose your admin username in place of `admin` if you like.

```bash
gcloud run deploy scholarforge \
  --source . \
  --service-account scholarforge-run@scholarforge-84902.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=scholarforge-84902,AI_PROVIDER=huggingface,ADMIN_USERNAME=admin,DASHBOARD_TZ=Asia/Bangkok \
  --set-secrets HF_TOKEN=hf-token:latest,ADMIN_PASSWORD_HASH=admin-password-hash:latest \
  --memory 512Mi --min-instances 0 --max-instances 3
```

The first deploy takes a few minutes (Cloud Build builds the Dockerfile). At the end it prints a URL like `https://scholarforge-xxxxx.asia-southeast1.run.app`.

## 8. Check it works

1. Open the URL → **Sign up** as a normal student and check **Settings** → *AI assistant* says **Ready**.
2. Create a project, search for papers, open one and ask a question.
3. Open `https://…run.app/admin` → sign in with the **admin** username and password → the usage dashboard shows the activity from step 2.

## Updating, logs, switching off

| Task | Command |
|---|---|
| Deploy a new version | run the step 7 command again |
| Read server logs | `gcloud run services logs read scholarforge --limit 100` |
| Change the admin password | make a new hash (step 6), then `printf '%s' 'HASH' \| gcloud secrets versions add admin-password-hash --data-file=-` and run the deploy command again |
| Use a different AI model | `gcloud run services update scholarforge --update-env-vars HF_CHAT_MODEL=org/model` |
| Take the site offline | `gcloud run services delete scholarforge` |

## Costs to watch

- **Cloud Run:** scales to zero when nobody uses it. A class-sized app normally stays in the free tier.
- **Firestore:** every request writes one `access_log` entry. The free quota is 20,000 writes/day, which is plenty for a class.
- **Hugging Face:** pay per use. Search embeds ~30 texts per search (one batched call). Each question, summary or outline is one chat call. Watch your usage at https://huggingface.co/settings/billing.

## Troubleshooting

| You see | Likely cause |
|---|---|
| "The AI service isn't responding right now" | HF token missing or wrong, no credits left, or the model is unavailable. Check the server logs for `hf.chat.error status=...` |
| Pages fail with 403 / PermissionDenied in logs | step 5 role missing for the service account |
| `/admin/login` says "isn't set up yet" | `ADMIN_USERNAME` or the `admin-password-hash` secret is missing from the deploy command |
| "Too many failed attempts" | 5 wrong passwords from your network — wait 15 minutes |
| Signed out after every click | `COOKIE_SECURE=true` but the site was opened over plain http — always use the https URL |

## Privacy notes (PDPA)

- The Terms page (v1.1) now says that search text, paper abstracts and questions are sent to Hugging Face in the hosted version. Email and password are never sent.
- **Existing accounts agreed to v1.0**, which said no data goes to an external AI service. Before real users rely on the hosted version, show them the new terms and record their agreement again (a re-consent step is not built yet).
- The dashboard shows totals only. The raw access log (user ID + IP) is personal data: only project owners should have Firestore access.
