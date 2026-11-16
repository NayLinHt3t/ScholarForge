"""Account clean-up tool for the person running ScholarForge.

Run from the project folder (it uses the same .env / Firestore as the app):

    python -m app.tools.users check                  # what's in the database, and why the dashboard may show 0
    python -m app.tools.users list                   # every account: email, created, projects
    python -m app.tools.users reset-password EMAIL   # set a new password (you type it)
    python -m app.tools.users delete EMAIL           # delete an account and all its projects (asks to confirm)

Consent records and the audit log are kept on purpose (legal requirement); every
reset/delete made here is written to the audit log.
"""
import getpass
import json
import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from google.cloud import firestore  # noqa: E402

from app.collections import ACCESS_LOG, PROJECTS, SESSIONS, USERS  # noqa: E402
from app.database import get_db  # noqa: E402
from app.services import auth as auth_service  # noqa: E402

MIN_PASSWORD = 8


def _fmt(ts) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if isinstance(ts, datetime) else "—"


def _count(q) -> int:
    try:
        return int(q.count().get()[0][0].value)
    except Exception:  # noqa: BLE001 — fall back to reading documents
        return len(list(q.get()))


def _projects_of(db, user_id: str) -> int:
    return _count(db.collection(PROJECTS).where(filter=firestore.FieldFilter("user_id", "==", user_id)))


def cmd_check(db) -> int:
    print("Firestore project :", os.environ.get("GOOGLE_CLOUD_PROJECT", "(not set!)"))
    key = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if key:
        try:
            with open(key) as f:
                info = json.load(f)
            print("Key file          :", key, f"(project {info.get('project_id')})")
        except OSError:
            print("Key file          :", key, "(NOT FOUND)")
    else:
        print("Key file          : (none — using your gcloud login / Cloud identity)")

    users = _count(db.collection(USERS))
    print(f"\nAccounts (users)  : {users}")

    batches = list(db.collection(ACCESS_LOG).order_by("last_ts", direction=firestore.Query.DESCENDING).limit(5).get())
    total_docs = _count(db.collection(ACCESS_LOG))
    print(f"Access-log documents: {total_docs} total")
    if batches:
        newest = batches[0].to_dict()
        authed = {e.get("user_id") for b in batches for e in (b.to_dict() or {}).get("entries", [])
                  if e.get("user_id") and e.get("user_id") != "unauthenticated" and not str(e.get("user_id")).startswith("admin:")}
        print(f"Newest batch      : {_fmt(newest.get('last_ts'))}, {newest.get('count')} requests")
        print(f"Signed-in users in the 5 newest batches: {len(authed)}")
    else:
        print("Newest batch      : none — the app has not saved any usage batches here yet")
    old_format = total_docs - _count(db.collection(ACCESS_LOG).where(filter=firestore.FieldFilter("count", ">", 0)))
    if old_format > 0:
        print(f"Old-format entries : {old_format} (from before batching; the dashboard ignores these)")

    print("\nWhat this means:")
    if users == 0:
        print("- No accounts in THIS database. The app you sign in to is using a different Firestore project/key.")
    if not batches:
        print("- No usage saved yet. Make sure the app runs the newest code (restart it / redeploy),")
        print("  sign in as a student, click around, then open /admin (it saves waiting entries first).")
    elif users and batches:
        print("- Data is there. If /admin still shows 0, the app serving /admin is not using this database,")
        print("  or it runs older code — restart it (or redeploy on Render).")
    return 0


def cmd_list(db) -> int:
    docs = list(db.collection(USERS).get())
    if not docs:
        print("No accounts in this database.")
        return 0
    rows = []
    for d in docs:
        data = d.to_dict() or {}
        rows.append((data.get("email", "?"), _fmt(data.get("created_at")), _projects_of(db, d.id), d.id))
    rows.sort(key=lambda r: r[1])
    w = max(len(r[0]) for r in rows)
    print(f"{'EMAIL'.ljust(w)}  {'CREATED':<20}  PROJECTS  USER ID")
    for email, created, n, uid in rows:
        print(f"{email.ljust(w)}  {created:<20}  {n:>8}  {uid}")
    print(f"\n{len(rows)} account(s)")
    return 0


def _find(db, email: str):
    user = auth_service.get_user_by_email(db, email.strip().lower())
    if not user:
        print(f"No account with email {email!r}. Run `list` to see the exact emails.")
    return user


def cmd_reset_password(db, email: str) -> int:
    user = _find(db, email)
    if not user:
        return 1
    pw = getpass.getpass(f"New password for {user.email} (min {MIN_PASSWORD} characters): ")
    if len(pw) < MIN_PASSWORD:
        print("Too short.")
        return 1
    if getpass.getpass("Type it again: ") != pw:
        print("The two passwords don't match.")
        return 1
    db.collection(USERS).document(user.id).update({"password_hash": auth_service._hash_password(pw)})
    # sign the account out everywhere
    for s in db.collection(SESSIONS).where(filter=firestore.FieldFilter("user_id", "==", user.id)).get():
        s.reference.delete()
    auth_service._write_audit(db, action="password_reset_by_operator", user_id=user.id)
    print(f"Password changed for {user.email}. You can sign in with it now.")
    return 0


def cmd_delete(db, email: str) -> int:
    user = _find(db, email)
    if not user:
        return 1
    n = _projects_of(db, user.id)
    print(f"This permanently deletes {user.email} and its {n} project(s) with all papers, notes and outlines.")
    print("Consent records and the audit log are kept (legal requirement). This cannot be undone.")
    if input(f"Type the email again to confirm: ").strip().lower() != user.email:
        print("Not confirmed — nothing deleted.")
        return 1
    auth_service.delete_account(db, user.id)
    print(f"Deleted {user.email}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in {"check", "list", "reset-password", "delete"}:
        print(__doc__)
        return 1
    db = get_db()
    cmd = argv[0]
    if cmd == "check":
        return cmd_check(db)
    if cmd == "list":
        return cmd_list(db)
    if len(argv) < 2:
        print(f"Usage: python -m app.tools.users {cmd} EMAIL")
        return 1
    return cmd_reset_password(db, argv[1]) if cmd == "reset-password" else cmd_delete(db, argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
