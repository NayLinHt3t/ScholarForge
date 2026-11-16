"""Firestore collection name constants.

Top-level collections:   users, sessions, projects, consent_records, audit_log
Subcollections (under projects/{id}):
  saved_resources, outlines,
  evidence, notes, themes, claims, outline_sections
"""

USERS = "users"
SESSIONS = "sessions"
PROJECTS = "projects"
CONSENT_RECORDS = "consent_records"
AUDIT_LOG = "audit_log"
ADMIN_SESSIONS = "admin_sessions"      # admin portal sessions (token hash only), TTL on expire_at
ACCESS_LOG = "access_log"            # every request, 91-day TTL (see app/monitoring.py)

# Project subcollections
SAVED_RESOURCES = "saved_resources"   # sources (kept name for backward compat)
OUTLINES = "outlines"                  # AI-generated outlines (legacy/P1)
EVIDENCE = "evidence"
NOTES = "notes"
THEMES = "themes"
CLAIMS = "claims"
OUTLINE_SECTIONS = "outline_sections"
