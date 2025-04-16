import requests
from fastapi import Request, Body
from core.config import payu_settings
from fastapi.responses import JSONResponse
async def verifyPayment(request: Request,body: dict = Body(
        example={
            "txnid": "1234"
        }
    )):
    """Verify payment using PayU API"""
    try:
        # Parse JSON body
        data = request.json()
        txnid = data.get("txnid")

        if not txnid:
            return JSONResponse({"msg": "Transaction ID is required"}, status_code=400)

        # PayU Merchant Credentials
        PAYU_KEY = payu_settings.PAYU_KEY
        PAYU_SALT = payu_settings.PAYU_SALT

        # API Endpoint for Payment Verification (Use Live URL in Production)
        PAYU_VERIFY_URL = "https://test.payu.in/merchant/postservice?form=2"

        # Prepare the payload
        payload = {
            "key": PAYU_KEY,
            "command": "verify_payment",
            "var1": txnid,  # Transaction ID to verify
            "hash": "",  # Hash will be calculated below
        }

        import hashlib

        # Generate Hash (Using SHA-512)
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
            return JSONResponse(
                {"msg": "Payment verified", "data": response_data},
                status_code=200,
            )
        else:
            return JSONResponse(
                {"msg": "Payment verification failed", "data": response_data},
                status_code=400,
            )

    except Exception as err:
        return JSONResponse({"msg": "Error", "error": str(err)}, status_code=500)