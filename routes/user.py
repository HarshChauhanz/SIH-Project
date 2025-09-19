# from fastapi import APIRouter, Request, Form, Depends, File, UploadFile
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.templating import Jinja2Templates
# from service.firebase_service import get_current_user
# from fastapi.responses import RedirectResponse
# from firebase_admin import auth
# from fastapi import APIRouter, HTTPException
# from service.firebase_service import db

# router = APIRouter()
# templates = Jinja2Templates(directory="templates")

# @router.get("/user/me")
# async def get_user(request: Request, current_user: str = Depends(get_current_user)):
#     if current_user is None:
#         raise HTTPException(status_code=401, detail="Not authenticated")

#     try:
#         user = auth.get_user(current_user)  # Fetch user using session's user ID
#         return {"display_name": user.display_name}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, Request, Form, Depends, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from service.firebase_service import get_current_user
from fastapi.responses import RedirectResponse
from firebase_admin import auth
from fastapi import APIRouter, HTTPException
from service.firebase_service import db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/user/me")
async def get_user(request: Request, current_user: str = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        user = auth.get_user(current_user)
        return {"display_name": user.display_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/student/dashboard", response_class=HTMLResponse)
async def student_dashboard(request: Request, current_user: str = Depends(get_current_user)):
    if current_user is None:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("student_dashboard.html", {"request": request})

@router.get("/user/mentor/dashboard", response_class=HTMLResponse)
async def mentor_dashboard(request: Request, current_user: str = Depends(get_current_user)):
    if current_user is None:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("mentor_dashboard.html", {"request": request})

@router.get("/user/guardian/dashboard", response_class=HTMLResponse)
async def guardian_dashboard(request: Request, current_user: str = Depends(get_current_user)):
    if current_user is None:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("guardian_dashboard.html", {"request": request})
