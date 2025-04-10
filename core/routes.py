from fastapi import APIRouter
from payments.paymentRoutes import payment_router
from users.userRoutes import user_router
from sliders.sliderRoutes import slider_router

api_router = APIRouter()

# Include all feature routers
api_router.include_router(payment_router)
api_router.include_router(user_router)
api_router.include_router(slider_router)