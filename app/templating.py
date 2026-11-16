"""Single shared Jinja2Templates instance, with helpers every template can use."""
from fastapi.templating import Jinja2Templates

from app import config
from app.clients import ai

templates = Jinja2Templates(directory="app/templates")


def is_admin(user) -> bool:
    return bool(user) and getattr(user, "email", "").lower() in config.ADMIN_EMAILS


templates.env.globals["ai_runs_locally"] = ai.runs_locally
templates.env.globals["ai_unavailable_message"] = ai.unavailable_message
templates.env.globals["is_admin"] = is_admin
