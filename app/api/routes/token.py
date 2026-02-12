from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

# Create router instance for grouping related endpoints
router = APIRouter()

@router.get("/token", response_class=JSONResponse)
async def get_token(request: Request):
    """
    DEVELOPMENT ONLY:
    Return the backend-generated API token to the frontend.
    WARNING: Insure since token exposed
    """
    token = request.app.state.API_TOKEN
    return {"token": token}