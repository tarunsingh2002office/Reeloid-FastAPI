import os
from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import paidMintsBuyerCollection

async def paymentError(request: Request):
    
    # Extract form data
    form_data = await request.form()
    txnid = form_data.get("txnid")
    mihpayid = form_data.get("mihpayid", "")
    bank_ref_num = form_data.get("bank_ref_num", "")
    paymentMode = form_data.get("mode", "")
    netAmountDeducted = form_data.get("net_amount_debit", "")
    paymentGateway = form_data.get("PG_TYPE", "")
    paymentAggregator = form_data.get("pa_name", "")
    error_message = form_data.get("error_Message", "Payment Failed")

    try:
        # Update the database
        paidMintsPlan = paidMintsBuyerCollection.find_one_and_update(
            {"txnid": str(txnid)},
            {
                "$set": {
                    "status": "Failed",
                    "mihpayid": mihpayid,
                    "Deductable_Amount": netAmountDeducted,
                    "paymentSource": "Payu",
                    "paymentMode": paymentMode,
                    "bank_ref_num": bank_ref_num,
                    "netAmountDeducted": netAmountDeducted,
                    "paymentGateway": paymentGateway,
                    "paymentAggregator": paymentAggregator,
                    "error_message": error_message,
                }
            },
        )
        if not paidMintsPlan:
            raise Exception("Transaction ID not found in database.")
        
        return JSONResponse(
            {"msg": "payment Failed", "txnid": txnid, "error_message": error_message},
            status_code=200,
        )
    except Exception as err:
        return JSONResponse({"msg": str(err)}, status_code=400)