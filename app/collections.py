"""Firestore collection name constants.

Top-level collections:   users, sessions, projects, consent_records, audit_log
Subcollections (under projects/{id}):  saved_resources, outlines
"""

USERS = "users"
SESSIONS = "sessions"
PROJECTS = "projects"
SAVED_RESOURCES = "saved_resources"
OUTLINES = "outlines"
CONSENT_RECORDS = "consent_records"
AUDIT_LOG = "audit_log"
