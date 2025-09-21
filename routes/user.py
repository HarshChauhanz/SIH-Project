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
#         user = auth.get_user(current_user)
#         return {"display_name": user.display_name}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/user/student/dashboard", response_class=HTMLResponse)
# async def student_dashboard(request: Request, current_user: str = Depends(get_current_user)):
#     if current_user is None:
#         return RedirectResponse(url="/login")
    
#     user_ref = db.collection("users").document(current_user)
#     user_doc = user_ref.get()
    
#     if not user_doc.exists or user_doc.to_dict().get("role") != "student":
#         raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this page.")
        
#     user_name = user_doc.to_dict().get("name", "Student")
    
#     return templates.TemplateResponse("student_dashboard.html", {"request": request, "user_name": user_name})

# @router.get("/user/mentor/dashboard", response_class=HTMLResponse)
# async def mentor_dashboard(request: Request, current_user: str = Depends(get_current_user)):
#     if current_user is None:
#         return RedirectResponse(url="/login")
        
#     user_ref = db.collection("users").document(current_user)
#     user_doc = user_ref.get()
    
#     if not user_doc.exists or user_doc.to_dict().get("role") != "mentor":
#         raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this page.")
        
#     user_name = user_doc.to_dict().get("name", "Mentor")
        
#     return templates.TemplateResponse("mentor_dashboard.html", {"request": request, "user_name": user_name})

# @router.get("/user/guardian/dashboard", response_class=HTMLResponse)
# async def guardian_dashboard(request: Request, current_user: str = Depends(get_current_user)):
#     if current_user is None:
#         return RedirectResponse(url="/login")

#     user_ref = db.collection("users").document(current_user)
#     user_doc = user_ref.get()
    
#     if not user_doc.exists or user_doc.to_dict().get("role") != "guardian":
#         raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this page.")
        
#     user_name = user_doc.to_dict().get("name", "Guardian")

#     return templates.TemplateResponse("guardian_dashboard.html", {"request": request, "user_name": user_name})

# # from fastapi import APIRouter, Request, Form, Depends, File, UploadFile
# # from fastapi.responses import HTMLResponse, JSONResponse
# # from fastapi.templating import Jinja2Templates
# # from service.firebase_service import get_current_user
# # from fastapi.responses import RedirectResponse
# # from firebase_admin import auth
# # from fastapi import APIRouter, HTTPException
# # from service.firebase_service import db

# # router = APIRouter()
# # templates = Jinja2Templates(directory="templates")

# # @router.get("/user/me")
# # async def get_user(request: Request, current_user: str = Depends(get_current_user)):
# #     if current_user is None:
# #         raise HTTPException(status_code=401, detail="Not authenticated")

# #     try:
# #         user = auth.get_user(current_user)
# #         return {"display_name": user.display_name}
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=str(e))

# # @router.get("/user/student/dashboard", response_class=HTMLResponse)
# # async def student_dashboard(request: Request, current_user: str = Depends(get_current_user)):
# #     if current_user is None:
# #         return RedirectResponse(url="/login")
# #     return templates.TemplateResponse("student_dashboard.html", {"request": request})

# # @router.get("/user/mentor/dashboard", response_class=HTMLResponse)
# # async def mentor_dashboard(request: Request, current_user: str = Depends(get_current_user)):
# #     if current_user is None:
# #         return RedirectResponse(url="/login")
# #     return templates.TemplateResponse("mentor_dashboard.html", {"request": request})

# # @router.get("/user/guardian/dashboard", response_class=HTMLResponse)
# # async def guardian_dashboard(request: Request, current_user: str = Depends(get_current_user)):
# #     if current_user is None:
# #         return RedirectResponse(url="/login")
# #     return templates.TemplateResponse("guardian_dashboard.html", {"request": request})


from fastapi import APIRouter, Request, Form, Depends, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from service.firebase_service import get_current_user
from fastapi.responses import RedirectResponse
from firebase_admin import auth
from fastapi import APIRouter, HTTPException
from service.firebase_service import db
from predict import predict_risk, batch_predict_risk # Import the prediction functions
import pandas as pd

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
    
    user_ref = db.collection("users").document(current_user)
    user_doc = user_ref.get()
    
    if not user_doc.exists or user_doc.to_dict().get("role") != "student":
        raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this page.")
        
    user_name = user_doc.to_dict().get("name", "Student")
    
    return templates.TemplateResponse("student_dashboard.html", {"request": request, "user_name": user_name})

@router.get("/user/mentor/dashboard", response_class=HTMLResponse)
async def mentor_dashboard(request: Request, current_user: str = Depends(get_current_user)):
    if current_user is None:
        return RedirectResponse(url="/login")

    user_ref = db.collection("users").document(current_user)
    user_doc = user_ref.get()

    if not user_doc.exists or user_doc.to_dict().get("role") != "mentor":
        raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this page.")

    user_name = user_doc.to_dict().get("name", "Mentor")

    # --- New: Analyze sample student data ---
    # test_data = [
    #     {'Student_ID': 'RJC00001', 'Institution_Type': 'College', 'State': 'Rajasthan', 'Academic_Year': '2024-25', 'District': 'Jodhpur', 'Age': 21, 'Gender': 'Male', 'Area_Type': 'Rural', 'Social_Category': 'OBC', 'Education_Level': 'Undergraduate', 'Program': 'Bachelor of Arts (BA)', 'Affiliated_University': 'Jai Narain Vyas University, Jodhpur', 'College_Type': 'Private College', 'Mother_Education': 'Primary', 'Father_Education': 'Secondary', 'Family_Income_Monthly': '10000-20000', 'Medium_of_Instruction': 'Hindi', 'Attendance_Percentage': 80.45, 'Current_Academic_Score': 86.0, 'Previous_Year_Score': 98.0, 'First_Semester_Grade': 80.86, 'Second_Semester_Grade': 82.16, 'Fee_Payment_Status': 'Up_to_Date', 'Scholarship_Status': 'Yes', 'Financial_Assistance': 'Not_Received', 'Disciplinary_Records': 'No', 'Extracurricular_Participation': 'Active', 'Library_Usage': 'Regular'},
    #     {'Student_ID': 'RJC00002', 'Institution_Type': 'College', 'State': 'Rajasthan', 'Academic_Year': '2024-25', 'District': 'Churu', 'Age': 18, 'Gender': 'Male', 'Area_Type': 'Rural', 'Social_Category': 'OBC', 'Education_Level': 'Postgraduate', 'Program': 'Bachelor of Arts (BA)', 'Affiliated_University': 'Jai Narain Vyas University, Jodhpur', 'College_Type': 'Private College', 'Mother_Education': 'Illiterate', 'Father_Education': 'Secondary', 'Family_Income_Monthly': '5000-10000', 'Medium_of_Instruction': 'English', 'Attendance_Percentage': 78.39, 'Current_Academic_Score': 56.7, 'Previous_Year_Score': 47.57, 'First_Semester_Grade': 49.58, 'Second_Semester_Grade': 50.21, 'Fee_Payment_Status': 'Up_to_Date', 'Scholarship_Status': 'Yes', 'Financial_Assistance': 'Not_Received', 'Disciplinary_Records': 'No', 'Extracurricular_Participation': 'Limited', 'Library_Usage': 'Occasional'},
    #     {'Student_ID': 'RJC00006', 'Institution_Type': 'College', 'State': 'Rajasthan', 'Academic_Year': '2024-25', 'District': 'Jaipur', 'Age': 21, 'Gender': 'Female', 'Area_Type': 'Urban', 'Social_Category': 'SC', 'Education_Level': 'Undergraduate', 'Program': 'Bachelor of Technology (BTech)', 'Affiliated_University': 'Rajasthan Technical University, Kota', 'College_Type': 'Private College', 'Mother_Education': 'Illiterate', 'Father_Education': 'Primary', 'Family_Income_Monthly': '20000-50000', 'Medium_of_Instruction': 'English', 'Attendance_Percentage': 82.56, 'Current_Academic_Score': 91.8, 'Previous_Year_Score': 98.0, 'First_Semester_Grade': 91.14, 'Second_Semester_Grade': 100.0, 'Fee_Payment_Status': 'Pending', 'Scholarship_Status': 'No', 'Financial_Assistance': 'Not_Received', 'Disciplinary_Records': 'No', 'Extracurricular_Participation': 'Active', 'Library_Usage': 'Occasional'}
    # ]


    df = pd.read_csv("test_data.csv")
    test_data = df.to_dict(orient='records')


    predictions = batch_predict_risk(test_data)
    risk_summary = pd.Series([p.get('risk_level', 'Error') for p in predictions]).value_counts().to_dict()


    return templates.TemplateResponse("mentor_dashboard.html", {
        "request": request,
        "user_name": user_name,
        "risk_summary": risk_summary
    })


@router.post("/predict")
async def predict(request: Request):
    data = await request.json()
    prediction = predict_risk(data)
    return JSONResponse(content=prediction)