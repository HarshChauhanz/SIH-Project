import os
import firebase_admin
from firebase_admin import auth, credentials, firestore
import requests
from dotenv import load_dotenv
from fastapi import Request

load_dotenv()

if not firebase_admin._apps:
    # Make sure the path to your service account key is correct
    cred = credentials.Certificate("D:\Project\SIH\serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
FIREBASE_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

async def get_current_user(request: Request):
    session_token = request.cookies.get("session")
    if not session_token:
        return None
    try:
        decoded_token = auth.verify_id_token(session_token)
        return decoded_token.get("uid")
    except Exception:
        return None

async def create_user_in_auth(email: str, password: str, name: str, role: str):
    """
    Quickly creates a user in Firebase Auth and Firestore.
    Returns a result dictionary.
    """
    try:
        user = auth.create_user(email=email, password=password, display_name=name)
        db.collection("users").document(user.uid).set({
            "user_id": user.uid,
            "email": email,
            "name": name,
            "role": role
        })
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

async def send_verification_email(email: str, password: str):
    """
    Sends the verification email. This is the slow part that will run in the background.
    """
    try:
        signin_request = {"email": email, "password": password, "returnSecureToken": True}
        signin_response = requests.post(FIREBASE_SIGNIN_URL, json=signin_request).json()
        id_token = signin_response.get("idToken")

        if id_token:
            firebase_email_api = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
            email_request = {"requestType": "VERIFY_EMAIL", "idToken": id_token}
            email_response = requests.post(firebase_email_api, json=email_request)
            if email_response.status_code != 200:
                print(f"Error sending verification email to {email}: {email_response.text}")
        else:
            print(f"Could not get ID token for {email} to send verification.")
    except Exception as e:
        print(f"Background task failed for sending verification email to {email}: {e}")

async def login_user(email: str, password: str):
    try:
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(FIREBASE_SIGNIN_URL, json=payload)

        if response.status_code == 200:
            data = response.json()
            user = auth.get_user_by_email(email)

            if not user.email_verified:
                return {"error": "Please verify your email before logging in."}

            return {
                "message": "Login successful",
                "idToken": data["idToken"],
                "refreshToken": data["refreshToken"],
                "userId": data["localId"]
            }
        else:
            return {"error": response.json().get("error", {}).get("message", "Login failed")}
    except Exception as e:
        return {"error": str(e)}

async def verify_google_token(token: str):
    try:
        decoded_token = auth.verify_id_token(token)
        return {
            "user_id": decoded_token["uid"],
            "email": decoded_token["email"],
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture")
        }
    except Exception as e:
        return {"error": str(e)}
    
    
# import os
# import firebase_admin
# from firebase_admin import auth, credentials, firestore
# import requests
# from dotenv import load_dotenv
# from fastapi import HTTPException
# from fastapi import Request
# from google.oauth2 import id_token
# import firebase_admin
# from firebase_admin import auth
# import requests


# load_dotenv()

# if not firebase_admin._apps:
#     cred = credentials.Certificate("D:\Project\Hackaccino-main\serviceAccountKey.json")
#     firebase_admin.initialize_app(cred)

# db = firestore.client()
# FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
# GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# FIREBASE_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"



# async def get_current_user(request: Request):
#     session_token = request.cookies.get("session")
#     if not session_token:
#         return None
    
#     try:
#         decoded_token = auth.verify_id_token(session_token)
#         user_id = decoded_token.get("uid")
#         return user_id
#     except Exception:
#         return None

# async def create_user(email: str, password: str, name: str, role: str):
#     try:
#         user = auth.create_user(email=email, password=password, display_name=name)
        
#         user_ref = db.collection("users").document(user.uid)
#         user_ref.set({
#             "user_id": user.uid,
#             "email": email,
#             "name": name,
#             "role": role
#         })

#         signin_request = {
#             "email": email,
#             "password": password,
#             "returnSecureToken": True
#         }
#         signin_response = requests.post(FIREBASE_SIGNIN_URL, json=signin_request).json()

#         id_token = signin_response.get("idToken")
#         if not id_token:
#             return {"error": "Failed to get ID token for email verification."}

#         firebase_email_api = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
#         email_request = {
#             "requestType": "VERIFY_EMAIL",
#             "idToken": id_token
#         }
#         email_response = requests.post(firebase_email_api, json=email_request)
        
#         if email_response.status_code == 200:
#             return {"status": "User created successfully. Verification email sent."}
#         else:
#             return {"error": f"Failed to send verification email: {email_response.json()}"}

#     except Exception as e:
#         return {"error": str(e)}

# async def login_user(email: str, password: str):
#     try:
#         payload = {
#             "email": email,
#             "password": password,
#             "returnSecureToken": True
#         }
#         response = requests.post(FIREBASE_SIGNIN_URL, json=payload)

#         if response.status_code == 200:
#             data = response.json()
#             user = auth.get_user_by_email(email)

#             if not user.email_verified:
#                 return {"error": "Please verify your email before logging in."}

#             return {
#                 "message": "Login successful",
#                 "idToken": data["idToken"],      
#                 "refreshToken": data["refreshToken"], 
#                 "userId": data["localId"]
#             }
#         else:
#             return {"error": response.json().get("error", {}).get("message", "Login failed")}
#     except Exception as e:
#         return {"error": str(e)}

    
# async def verify_google_token(token: str):
#     try:
#         decoded_token = auth.verify_id_token(token) 
#         return {
#             "user_id": decoded_token["uid"],  
#             "email": decoded_token["email"],
#             "name": decoded_token.get("name"),
#             "picture": decoded_token.get("picture")
#         }
#     except Exception as e:
#         return {"error": str(e)}