from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

# Create router instance for grouping related endpoints
router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# Home page
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    api_token = request.app.state.API_TOKEN
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "api_token": api_token}
    )