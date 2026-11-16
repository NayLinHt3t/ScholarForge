"""Single shared Jinja2Templates instance, with helpers every template can use."""
from fastapi.templating import Jinja2Templates

from app.clients import ai

templates = Jinja2Templates(directory="app/templates")


templates.env.globals["ai_runs_locally"] = ai.runs_locally
templates.env.globals["ai_unavailable_message"] = ai.unavailable_message
