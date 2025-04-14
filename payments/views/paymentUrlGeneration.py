import time
import random
import hashlib
from bson import ObjectId
from fastapi import Request
from datetime import datetime
from fastapi.responses import JSONResponse
from core.database import paidMintsBuyerCollection, mintsPlanCollection
from core.config import PAYUSettings
# Load environment variables
PAYU_KEY = PAYUSettings.PAYU_KEY
PAYU_SALT = PAYUSettings.PAYU_SALT
PAYU_URL = PAYUSettings.PAYU_URL


def generate_hash(data):
    """Generate PayU hash using SHA-512 with the correct parameter sequence"""
    hash_string = f"{PAYU_KEY}|{data['txnid']}|{data['amount']}|{data['productinfo']}|{data['firstname']}|{data['email']}|||||||||||{PAYU_SALT}"
    return hashlib.sha512(hash_string.encode()).hexdigest()


async def paymentUrlGeneration(request: Request):
    """Generate PayU Payment Request"""
    try:
        # Parse JSON body
        data = await request.json()
        packageId = data.get("pid")
        userId = request.state.userId  # Assuming userId is passed in the request body
        txnid = f"TXN{int(time.time() * 1000)}{random.randint(1000, 9999)}"

        email = data.get("email")
        phone = data.get("phone")
        firstname = data.get("firstname")
        productinfo = data.get("productinfo") or "not provided"

        # Ensure all required parameters are included
        if not txnid:
            return JSONResponse({"msg": "invalid txn id"}, status_code=400)

        # Fetch package details from the database
        mintsDetails = mintsPlanCollection.find_one({"_id": ObjectId(packageId)})
        if not mintsDetails:
            return JSONResponse({"msg": "invalid package id"}, status_code=400)

        Price = mintsDetails.get("Price")
        hash_data = {
            "key": PAYU_KEY,
            "txnid": txnid,
            "amount": Price,
            "quantity": mintsDetails.get("Quantity"),
            "productinfo": productinfo,
            "firstname": firstname,
            "email": email,
            "phone": phone,
            "surl": "http://192.168.1.14:8000/payment/success/",
            "furl": "http://192.168.1.14:8000/payment/error/",
        }
        hash_data["hash"] = generate_hash(hash_data)

        # Save transaction details in the database
        try:
            paidMintsBuyerCollection.insert_one(
                {
                    "userId": userId,
                    "txnid": txnid,
                    "amount": Price,
                    "date": datetime.now(),
                    "quantity": mintsDetails.get("Quantity"),
                    "status": "Pending",
                }
            )
            return JSONResponse(
                {"payu_url": PAYU_URL, "params": hash_data}, status_code=200
            )
        except Exception as err:
            return JSONResponse(
                {"error": "Error while saving transaction data in database"},
                status_code=500,
            )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)