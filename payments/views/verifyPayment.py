import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from dotenv import load_dotenv


@csrf_exempt
def verifyPayment(request):
    if request.method == "POST":  # Use POST instead of GET
        try:
            # Get txnid from request
            # data = json.loads(request.body)
            txnid = request.POST.get("txnid")

            if not txnid:
                return JsonResponse({"msg": "Transaction ID is required"}, status=400)

            # PayU Merchant Credentials
            PAYU_KEY = os.getenv("PAYU_KEY")
            PAYU_SALT = os.getenv("PAYU_SALT")

            # API Endpoint for Payment Verification (Use Live URL in Production)
            PAYU_VERIFY_URL = "https://test.payu.in/merchant/postservice?form=2"

            # Prepare the payload
            payload = {
                "key": PAYU_KEY,
                "command": "verify_payment",
                "var1": txnid,  # Transaction ID to verify
                "hash": "",  # Hash will be calculated below
            }

            # Generate Hash (Using SHA-512)
            import hashlib

            hash_string = f"{PAYU_KEY}|verify_payment|{txnid}|{PAYU_SALT}"
            hashh = hashlib.sha512(hash_string.encode()).hexdigest()
            payload["hash"] = hashh  # Assign hash to payload

            # Send the request
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(PAYU_VERIFY_URL, data=payload, headers=headers)

            # Parse the response
            response_data = response.json()

            # Check response status
            if response_data.get("status") == 1:

                return JsonResponse(
                    {"msg": "Payment verified", "data": response_data},
                    status=200,
                )
            else:
                return JsonResponse(
                    {"msg": "Payment verification failed", "data": response_data},
                    status=400,
                )

        except Exception as err:
            return JsonResponse({"msg": "Error", "error": str(err)}, status=500)

    return JsonResponse({"msg": "Invalid request method"}, status=405)
