"""Create the bcrypt hash for the admin portal password.

    python -m app.tools.admin_password

Type the password twice (it is not shown). Put the printed line in your .env
(or in the Secret Manager secret `admin-password-hash` when hosted).
The plain password is never saved anywhere.
"""
import getpass
import sys

from app.services.admin_auth import hash_password

MIN_LENGTH = 12


def main() -> int:
    pw = getpass.getpass("New admin password (min 12 characters): ")
    if len(pw) < MIN_LENGTH:
        print(f"Too short — use at least {MIN_LENGTH} characters.", file=sys.stderr)
        return 1
    if getpass.getpass("Type it again: ") != pw:
        print("The two passwords don't match.", file=sys.stderr)
        return 1
    h = hash_password(pw)
    print("\nAdd this line to .env (keep the single quotes):\n")
    print(f"ADMIN_PASSWORD_HASH='{h}'")
    print("\nOr, for Cloud Run, store it as a secret:\n")
    print(f"printf '%s' '{h}' | gcloud secrets create admin-password-hash --data-file=-")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
