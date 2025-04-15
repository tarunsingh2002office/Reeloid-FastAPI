from typing import List
from fastapi import Header
from pydantic import BaseModel
from datetime import datetime

# USER
class CreateUserRequest(BaseModel):
    email: str
    name: str
    password: str
    confirmPassword: str
class SignInRequest(BaseModel):
    email: str
    password: str
class GenreSelectionRequest(BaseModel): # token
    selectedGenre: List[str] 
class UsersLanguaseSelectionRequest(BaseModel): # token
    selectedLanguages: List[str]
class EditProfileDetailsRequest(BaseModel): # token
    name: str
    email: str
    gender: str
    mobile: str
# class dailyCheckInTaskRequest(BaseModel): # token  -> edit + otp
class CollectCheckInPointRequest(BaseModel): # token
    taskId: str
class MarkAsBookMarkRequest(BaseModel): # token
    shortsId: str
class LikeVideoRequest(BaseModel): # token
    shortsId: str
    reactionType: str
class GoogleAuthRequest(BaseModel): # token
    fcmtoken: str
    deviceType: str
    authToken: str
class forgotPasswordAPIRequests(BaseModel): 
    email: str
class VerifyOtpRequest(BaseModel): 
    otp: str
class UpdatePasswordRequest(BaseModel): # token
    password: str
    confirmPassword: str
class ContinueWatchingHistorySavingRequest(BaseModel): # token
    moviesId: str
    currentShortsId: str
    timestamp: str
# Payments
class PaymentUrlGenerationRequest(BaseModel): # token
    email: str
    phone: str
    firstname:str
    productinfo: str
    pid: str
class PaymentErrorRequest(BaseModel): # token
    txnid: str
    mihpayid: str
    bank_ref_num:str
    mode: str
    net_amount_debit: str
    PG_TYPE: str
    pa_name: str
    error_Message: str
    PaymentFailed: str
class PaymentSuccessRequest(BaseModel): # token
    txnid: str
    mihpayid: str
    bank_ref_num:str
    mode: str
    net_amount_debit: str
    PG_TYPE: str
    pa_name: str
class VerifyPaymentRequest(BaseModel): # token
    txnid: str
    
# Slider
class GetMovieDataRequest(BaseModel): # token
    movieID: str
class PurchasePremiumVideoRequest(BaseModel): # token
    shortsID: str
class RefreshTheVideoURLRequest(BaseModel): # token
    url: str
def get_current_user(token: str = Header(..., description="User authentication token")):
    """
    Dependency to document the token header in Swagger UI.
    The actual token validation and extraction are handled by the middleware.
    """
    return token

class GetLikedVideoRequest(BaseModel):
    shortsId: List[str]