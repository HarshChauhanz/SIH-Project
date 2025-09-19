from fastapi import APIRouter, Request, Form, Depends, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from firebase_admin import auth, firestore

# Correctly import the new functions from the service
from service.firebase_service import create_user_in_auth, send_verification_email, login_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")
db = firestore.client()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, role: str = ""):
    error = request.query_params.get("error", "")
    status = request.query_params.get("status", "")
    return templates.TemplateResponse("login.html", {"request": request, "error": error, "status": status, "role": role})

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    error = request.query_params.get("error", "")
    return templates.TemplateResponse("signup.html", {"request": request, "error": error})

@router.post("/signup/save")
async def signup(
    background_tasks: BackgroundTasks,  # FIX: Inject BackgroundTasks without Depends()
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...)
):
    # Step 1: Quickly create the user account
    result = await create_user_in_auth(email, password, name, role)

    if "error" in result:
        error_message = result["error"]
        if "INVALID_EMAIL" in error_message:
            error_message = "Invalid email address. Please try with valid email."
        elif "Invalid password string" in error_message:
            error_message = "Invalid password. Password must be a string at least 6 characters long."
        elif "EMAIL_EXISTS" in error_message:
            error_message = "The email is already registered. Try logging in."
        else:
            error_message = result["error"]
        return RedirectResponse(url=f"/signup?error={error_message}", status_code=303)

    # Step 2: Add the slow email task to run in the background
    background_tasks.add_task(send_verification_email, email, password)

    # Step 3: Immediately redirect the user with a success message
    success_message = "Your account has been created successfully. Please check your email to get started."
    return RedirectResponse(url=f"/login?status={success_message}", status_code=303)

@router.post("/login/save")
async def login(email: str = Form(...), password: str = Form(...), role: str = Form(...)):
    result = await login_user(email, password)
    
    if "error" in result:
        error_message = result["error"]
        if "INVALID_LOGIN_CREDENTIALS" in error_message:
            error_message = "Invalid email or password. Please try again."
        else:
            error_message = result["error"]
        return RedirectResponse(url=f"/login?error={error_message}&role={role}", status_code=303)

    user_id = result.get("userId")
    session_token = result.get("idToken", "") 

    if not session_token:
        return RedirectResponse(url=f"/login?error=InvalidSession&role={role}", status_code=303)

    user_ref = db.collection("users").document(user_id)
    user_data = user_ref.get()
    if user_data.exists:
        user_role = user_data.to_dict().get("role")
        if user_role == "student":
            response = RedirectResponse(url=f"/user/student/dashboard", status_code=303)
        elif user_role == "mentor":
            response = RedirectResponse(url=f"/user/mentor/dashboard", status_code=303)
        elif user_role == "guardian":
            response = RedirectResponse(url=f"/user/guardian/dashboard", status_code=303)
        else:
            response = RedirectResponse(url=f"/user/{user_id}/chat", status_code=303)
    else:
        response = RedirectResponse(url=f"/user/{user_id}/chat", status_code=303)

    response.set_cookie(key="session", value=session_token, httponly=True, max_age=604800)
    return response

@router.post("/login/google")
async def google_login(id_token: str = Form(...), role: str = Form(...)):
    try:
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]
        email = decoded_token.get("email")
        name = decoded_token.get("name", "")

        if not name:
            user_record = auth.get_user(user_id)
            name = user_record.display_name if user_record.display_name else "Unknown User"

        user_ref = db.collection("users").document(user_id)
        user_data = user_ref.get()

        if not user_data.exists:
            user_ref.set({
                "user_id": user_id,
                "email": email,
                "name": name,
                "role": role 
            })
            user_role = role
        else:
            user_role = user_data.to_dict().get("role")

        if user_role == "student":
            redirect_url = "/user/student/dashboard"
        elif user_role == "mentor":
            redirect_url = "/user/mentor/dashboard"
        elif user_role == "guardian":
            redirect_url = "/user/guardian/dashboard"
        else:
            redirect_url = f"/user/{user_id}/chat"

        response = JSONResponse(content={"redirect_url": redirect_url})
        response.set_cookie(key="session", value=id_token, httponly=True, max_age=604800, secure=True)
        return response
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("session")
    return response

# from fastapi import APIRouter, Request, Form, Depends
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from service.firebase_service import create_user, login_user
# from fastapi.responses import RedirectResponse
# from firebase_admin import auth
# from fastapi import APIRouter, HTTPException
# from firebase_admin import firestore
# from service.firebase_service import verify_google_token
# from fastapi.responses import JSONResponse

# router = APIRouter()
# templates = Jinja2Templates(directory="templates")
# db = firestore.client()

# @router.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request, role: str = ""):
#     error = request.query_params.get("error", "")
#     status = request.query_params.get("status", "")

#     return templates.TemplateResponse("login.html", {"request": request, "error": error, "status": status, "role": role})

# @router.get("/signup", response_class=HTMLResponse)
# async def signup_page(request: Request):
#     error = request.query_params.get("error", "")
#     return templates.TemplateResponse("signup.html", {"request": request, "error": error})

# @router.post("/signup/save")
# async def signup(name: str = Form(...), email: str = Form(...), password: str = Form(...), role: str = Form(...)):
#     result = await create_user(email, password, name, role)
    
#     if "error" in result:
#         error_message = result["error"]
#         if "INVALID_EMAIL" in error_message:
#             error_message = "Invalid email address. Please try with valid email."
#         elif "Invalid password string" in error_message:
#             error_message = "Invalid password. Password must be a string at least 6 characters long."
#         elif "EMAIL_EXISTS" in error_message:
#             error_message = "The email is already registered. Try logging in."
#         else:
#             error_message = result["error"]
    
#         return RedirectResponse(url=f"/signup?error={error_message}", status_code=303)
#     return RedirectResponse(url="/login?status=Your account has been created successfully. Please verify your email to get started", status_code=303)

# @router.post("/login/save")
# async def login(email: str = Form(...), password: str = Form(...), role: str = Form(...)):
#     result = await login_user(email, password)
    
#     if "error" in result:
#         error_message = result["error"]
#         if "INVALID_LOGIN_CREDENTIALS" in error_message:
#             error_message = "Invalid email or password. Please try again."
#         else:
#             error_message = result["error"]
            
#         return RedirectResponse(url=f"/login?error={error_message}&role={role}", status_code=303)

#     user_id = result.get("userId")
#     session_token = result.get("idToken", "") 

#     if not session_token:
#         return RedirectResponse(url=f"/login?error=InvalidSession&role={role}", status_code=303)

#     user_ref = db.collection("users").document(user_id)
#     user_data = user_ref.get()
#     if user_data.exists:
#         user_role = user_data.to_dict().get("role")
#         if user_role == "student":
#             response = RedirectResponse(url=f"/user/student/dashboard", status_code=303)
#         elif user_role == "mentor":
#             response = RedirectResponse(url=f"/user/mentor/dashboard", status_code=303)
#         elif user_role == "guardian":
#             response = RedirectResponse(url=f"/user/guardian/dashboard", status_code=303)
#         else:
#             response = RedirectResponse(url=f"/user/{user_id}/chat", status_code=303) # Fallback
#     else:
#         response = RedirectResponse(url=f"/user/{user_id}/chat", status_code=303) # Fallback

#     response.set_cookie(key="session", value=session_token, httponly=True, max_age=604800)
#     return response

# @router.post("/login/google")
# async def google_login(id_token: str = Form(...), role: str = Form(...)):
#     try:
#         decoded_token = auth.verify_id_token(id_token)
#         user_id = decoded_token["uid"]
#         email = decoded_token.get("email")
#         name = decoded_token.get("name", "")

#         if not name:
#             user_record = auth.get_user(user_id)
#             name = user_record.display_name if user_record.display_name else "Unknown User"

#         user_ref = db.collection("users").document(user_id)
#         user_data = user_ref.get()

#         if not user_data.exists:
#             user_ref.set({
#                 "user_id": user_id,
#                 "email": email,
#                 "name": name,
#                 "role": role 
#             })
#             user_role = role
#         else:
#             user_role = user_data.to_dict().get("role")


#         if user_role == "student":
#             redirect_url = "/user/student/dashboard"
#         elif user_role == "mentor":
#             redirect_url = "/user/mentor/dashboard"
#         elif user_role == "guardian":
#             redirect_url = "/user/guardian/dashboard"
#         else:
#             redirect_url = f"/user/{user_id}/chat"


#         response = JSONResponse(content={"redirect_url": redirect_url})
#         response.set_cookie(key="session", value=id_token, httponly=True, max_age=604800, secure=True)
#         return response

#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=400)


# @router.get("/logout")
# async def logout():
#     response = RedirectResponse(url="/")
#     response.delete_cookie("session")
#     return response