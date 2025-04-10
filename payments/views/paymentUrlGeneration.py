import hashlib
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from streaming_app_backend.mongo_client import (
    paidMintsBuyerCollection,
    client,
    mintsPlanCollection,
)
from datetime import datetime
from bson import ObjectId
import time
import random
import os
from dotenv import load_dotenv
#  Use Correct Test Credentials
PAYU_KEY = os.getenv("PAYU_KEY")
PAYU_SALT = os.getenv("PAYU_SALT")
PAYU_URL = os.getenv("PAYU_URL")


def generate_hash(data):
    # """Generate PayU hash using SHA-512 with the correct parameter sequence"""
    hash_string = f"{PAYU_KEY}|{data['txnid']}|{data['amount']}|{data['productinfo']}|{data['firstname']}|{data['email']}|||||||||||{PAYU_SALT}"
    return hashlib.sha512(hash_string.encode()).hexdigest()


@csrf_exempt
def paymentUrlGeneration(request):
    # """Generate PayU Payment Request"""

    if request.method == "POST":

        try:
            data = json.loads(request.body)
            packageId = data.get("pid")
            userId = request.userId
            # txnid = data.get("txnid")  # Unique transaction ID
            txnid = f"TXN{int(time.time() * 1000)}{random.randint(1000, 9999)}"

            
            email = data.get("email")
            phone = data.get("phone")
            firstname = data.get("firstname")
            productinfo = data.get("productinfo") or "not provided"

            #  Ensure all required parameters are included
            if not txnid:
                return JsonResponse({"msg": "invalid txn id"}, status=400)
            # if not amount:
            #     return JsonResponse({"msg": "invalid amount"}, status=400)
            mintsDetails = mintsPlanCollection.find_one({"_id": ObjectId(packageId)})

            Price = mintsDetails.get("Price")
            hash_data = {
                "key": PAYU_KEY,
                "txnid": txnid,
                "amount": mintsDetails.get("Price"),
                "quantity": mintsDetails.get("Quantity"),
                "productinfo": productinfo,
                "firstname": firstname,
                "email": email,
                "phone": phone,
                "surl": "http://192.168.1.14:8000/payment/success/",
                "furl": "http://192.168.1.14:8000/payment/error/",
            }
            hash_data["hash"] = generate_hash(hash_data)
            try:
                
                
                paidMintsBuyerCollection.insert_one(
                    {
                        "userId": userId,
                        "txnid": txnid,
                        "amount": mintsDetails.get("Price"),
                        "date": datetime.now(),
                        "quantity": mintsDetails.get("Quantity"),
                        "status": "Pending",
                        # "couponApplied": "test100",
                    }
                )
                return JsonResponse(
                    {"payu_url": PAYU_URL, "params": hash_data}, status=200
                )
            except Exception as err:
                raise ValueError("err while saving transaction data in database")
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
