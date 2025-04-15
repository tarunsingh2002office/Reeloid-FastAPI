from fastapi import APIRouter
from payments.views.paymentUrlGeneration import paymentUrlGeneration
from payments.views.paymentError import paymentError
from payments.views.paymentSuccess import paymentSuccess
from payments.views.verifyPayment import verifyPayment


payment_router = APIRouter(prefix="/payment", tags=["Payments"])

# Payment routes
payment_router.add_api_route("/getUrl", paymentUrlGeneration, methods=["POST"])
payment_router.add_api_route("/error", paymentError, methods=["POST"])
payment_router.add_api_route("/success", paymentSuccess, methods=["POST"])
payment_router.add_api_route("/verify", verifyPayment, methods=["POST"])

payment_router.add_api_route("/getUrl/", paymentUrlGeneration, methods=["POST"])
payment_router.add_api_route("/error/", paymentError, methods=["POST"])
payment_router.add_api_route("/success/", paymentSuccess, methods=["POST"])
payment_router.add_api_route("/verify/", verifyPayment, methods=["POST"])