import time
import random
import hashlib
from bson import ObjectId
from fastapi import Depends, Request, Body
from datetime import datetime
from fastapi.responses import JSONResponse
from core.database import paidMintsBuyerCollection, mintsPlanCollection
from core.config import payu_settings
from helper_function.apis_requests import get_current_user
# Load environment variables
PAYU_KEY = payu_settings.PAYU_KEY
PAYU_SALT = payu_settings.PAYU_SALT
PAYU_URL = payu_settings.PAYU_URL


def generate_hash(data):
    """Generate PayU hash using SHA-512 with the correct parameter sequence"""
    hash_string = f"{PAYU_KEY}|{data['txnid']}|{data['amount']}|{data['productinfo']}|{data['firstname']}|{data['email']}|||||||||||{PAYU_SALT}"
    return hashlib.sha512(hash_string.encode()).hexdigest()


async def paymentUrlGeneration(request: Request, token: str = Depends(get_current_user),body: dict = Body(
        example={
            "email": "a@gmail.com",
            "phone": "1234567890",
            "firstname": "Mr. a",
            "productinfo": "Mint plan 1",
            "pid": "12334"
        }
    )):
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