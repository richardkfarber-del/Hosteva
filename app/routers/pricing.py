from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.core.billing_gate import is_billing_enabled

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/pricing")
def pricing_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pricing.html",
        context={
            "request": request,
            "billing_enabled": is_billing_enabled(),
        },
    )
