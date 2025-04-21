from fastapi import Request, Form
from fastapi.responses import JSONResponse
from core.database import paidMintsBuyerCollection
from core.config import payu_settings
async def paymentError(request: Request
    #                    ,body: dict = Body(...
    #     # example={
    #     #     "txnid": "12334",
    #     #     "mihpayid": "12334",
    #     #     "bank_ref_num": "12334",
    #     #     "mode": "12334",
    #     #     "net_amount_debit": "12334",
    #     #     "PG_TYPE": "12334",
    #     #     "pa_name": "12334",
    #     #     "error_Message": "12334",
    #     #     "PaymentFailed": "1234"
    #     # }
    # )
    ,txnid: str = Form(...),
    mihpayid: str = Form(""),
    bank_ref_num: str = Form(""),
    mode: str = Form(""),
    net_amount_debit: str = Form(""),
    PG_TYPE: str = Form(""),
    pa_name: str = Form(""),
    error_Message: str = Form("Payment Failed", alias="error_Message")
    ):
    PAYU_KEY = payu_settings.PAYU_KEY
    PAYU_SALT = payu_settings.PAYU_SALT
    # Extract form data
    headers = {"key": PAYU_KEY, "command": "verify_payment"}
    
    try:
        # Update the database
        paidMintsPlan = await paidMintsBuyerCollection.find_one_and_update(
            {"txnid": str(txnid)},
            {
                "$set": {
                    "status": "Failed",
                    "mihpayid": mihpayid,
                    "Deductable_Amount": net_amount_debit,
                    "paymentSource": "Payu",
                    "paymentMode": mode,
                    "bank_ref_num": bank_ref_num,
                    "netAmountDeducted": net_amount_debit,
                    "paymentGateway": PG_TYPE,
                    "paymentAggregator": pa_name,
                    "error_message": error_Message,
                }
            },
        )
        if not paidMintsPlan:
            raise Exception("Transaction ID not found in database.")
        
        return JSONResponse(
            {"msg": "payment Failed", "txnid": txnid, "error_message": error_Message},
            status_code=200,
        )
    except Exception as err:
        return JSONResponse({"msg": str(err)}, status_code=400)