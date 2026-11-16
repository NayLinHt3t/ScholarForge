"""Turn access-log entries into the numbers shown on the admin dashboard.

`summarize()` is a pure function (easy to test); `load()` reads Firestore.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from statistics import median
from zoneinfo import ZoneInfo

from google.cloud import firestore

from app.monitoring import ACCESS_LOG, UNAUTHENTICATED

MAX_ENTRIES = 50_000   # safety cap for one dashboard load


@dataclass
class DayStat:
    day: date
    users: int
    actions: int


@dataclass
class FeatureStat:
    label: str
    uses: int
    users: int


@dataclass
class Usage:
    days: int
    active_users: int = 0
    active_today: int = 0
    actions: int = 0
    signups: int = 0
    ai_calls: int = 0
    ai_median_ms: int | None = None
    ai_p95_ms: int | None = None
    ai_error_rate: float = 0.0
    daily: list[DayStat] = field(default_factory=list)
    hourly: list[int] = field(default_factory=lambda: [0] * 24)
    features: list[FeatureStat] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
    truncated: bool = False

    @property
    def busiest_hour(self) -> int | None:
        return max(range(24), key=lambda h: self.hourly[h]) if any(self.hourly) else None


def _pct(values: list[int], p: float) -> int:
    s = sorted(values)
    k = min(len(s) - 1, max(0, round(p * (len(s) - 1))))
    return s[k]


def summarize(entries: list[dict], days: int, now: datetime, tz: str, truncated: bool = False) -> Usage:
    zone = ZoneInfo(tz)
    today = now.astimezone(zone).date()
    first_day = today - timedelta(days=days - 1)
    u = Usage(days=days, truncated=truncated)

    users_by_day: dict[date, set] = defaultdict(set)
    actions_by_day: Counter = Counter()
    feature_uses: Counter = Counter()
    feature_users: dict[str, set] = defaultdict(set)
    all_users: set = set()
    ai_per_call: list[int] = []
    ai_calls = ai_errors = 0

    for e in entries:
        ts = e.get("ts")
        if not isinstance(ts, datetime):
            continue
        local = ts.astimezone(zone)
        d = local.date()
        if d < first_day or d > today:
            continue
        user = e.get("user_id") or UNAUTHENTICATED
        if str(user).startswith("admin:"):
            continue   # admin portal visits are not student usage
        authed = user != UNAUTHENTICATED
        feature = e.get("feature")
        status = int(e.get("status") or 0)

        if authed:
            users_by_day[d].add(user)
            all_users.add(user)
        if feature and status < 400:
            u.actions += 1
            actions_by_day[d] += 1
            u.hourly[local.hour] += 1
            feature_uses[feature] += 1
            if authed:
                feature_users[feature].add(user)
            if feature == "Sign up" and e.get("method") == "POST" and status in (302, 303):
                u.signups += 1

        calls = int(e.get("ai_calls") or 0)
        if calls:
            ai_calls += calls
            ai_errors += int(e.get("ai_errors") or 0)
            ok_calls = calls - int(e.get("ai_errors") or 0)
            if ok_calls > 0:
                ai_per_call.append(int(e.get("ai_ms") or 0) // calls)

        if status >= 500:
            u.errors.append({"ts": local, "route": e.get("route") or e.get("path"), "status": status})

    u.active_users = len(all_users)
    u.active_today = len(users_by_day.get(today, ()))
    u.daily = [
        DayStat(day=first_day + timedelta(days=i),
                users=len(users_by_day.get(first_day + timedelta(days=i), ())),
                actions=actions_by_day.get(first_day + timedelta(days=i), 0))
        for i in range(days)
    ]
    u.features = sorted(
        (FeatureStat(label=f, uses=n, users=len(feature_users[f])) for f, n in feature_uses.items()),
        key=lambda f: f.uses, reverse=True,
    )
    u.ai_calls = ai_calls
    if ai_per_call:
        u.ai_median_ms = int(median(ai_per_call))
        u.ai_p95_ms = _pct(ai_per_call, 0.95)
    u.ai_error_rate = (ai_errors / ai_calls) if ai_calls else 0.0
    u.errors = sorted(u.errors, key=lambda x: x["ts"], reverse=True)[:10]
    return u


def load(db: firestore.Client, days: int, now: datetime | None = None) -> tuple[list[dict], bool]:
    now = now or datetime.now(timezone.utc)
    since = now - timedelta(days=days + 1)   # +1 day so the first local day is complete
    docs = (
        db.collection(ACCESS_LOG)
        .where(filter=firestore.FieldFilter("ts", ">=", since))
        .limit(MAX_ENTRIES)
        .get()
    )
    entries = [d.to_dict() for d in docs]
    return entries, len(entries) >= MAX_ENTRIES


def count_collection(db: firestore.Client, name: str) -> int | None:
    try:
        result = db.collection(name).count().get()
        return int(result[0][0].value)
    except Exception:  # noqa: BLE001 — a missing number must not break the dashboard
        return None
