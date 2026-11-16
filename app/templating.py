"""Single shared Jinja2Templates instance, with helpers every template can use."""
from fastapi.templating import Jinja2Templates

from app.clients import ai

templates = Jinja2Templates(directory="app/templates")


templates.env.globals["ai_runs_locally"] = ai.runs_locally
templates.env.globals["ai_unavailable_message"] = ai.unavailable_message
templates.env.globals["ai_service_name"] = ai.service_name
templates.env.globals["ai_embeds_on_server"] = lambda: ai.embed_provider() == "local"
