from fastapi import Form, Request
from fastapi.responses import JSONResponse
from core.database import paidMintsBuyerCollection, client
from helper_function.addPointsToProfile import addPointsToProfile

async def paymentSuccess(request: Request
                        #  ,body: dict = Body(...
        # example={
        #     "txnid": "12334",
        #     "mihpayid": "12334",
        #     "bank_ref_num": "12334",
        #     "mode": "12334",
        #     "net_amount_debit": "12334",
        #     "PG_TYPE": "12334",
        #     "pa_name": "12334",
        # }
    # )
    ,txnid: str = Form(...),
    mihpayid: str = Form(""),
    bank_ref_num: str = Form(""),
    mode: str = Form(""),
    net_amount_debit: str = Form(""),
    PG_TYPE: str = Form(""),
    pa_name: str = Form("")
    ):
    # Extract form data
    # txnid = body.get("txnid")
    # mihpayid = body.get("mihpayid") or ""
    # bank_ref_num = body.get("bank_ref_num") or ""
    # paymentMode = body.get("mode") or ""
    # netAmountDeducted = body.get("net_amount_debit") or ""
    # paymentGateway = body.get("PG_TYPE") or ""
    # paymentAggregator = body.get("pa_name") or ""

    try:
        # Start a MongoDB session for transaction
        session = client.start_session()
        session.start_transaction()

        # Update the database
        paidMintsPlan = paidMintsBuyerCollection.find_one_and_update(
            {"txnid": str(txnid)},
            {
                "$set": {
                    "status": "Success",
                    "mihpayid": mihpayid,
                    "Deductable_Amount": net_amount_debit,
                    "paymentSource": "Payu",
                    "paymentMode": mode,
                    "bank_ref_num": bank_ref_num,
                    "netAmountDeducted": net_amount_debit,
                    "paymentGateway": PG_TYPE,
                    "paymentAggregator": pa_name,
                }
            },
            session=session,
        )

        if not paidMintsPlan:
            raise Exception("Transaction ID not found in database.")

        # Add points to the user's profile
        addPointsToProfile(
            paidMintsPlan.get("userId"), paidMintsPlan.get("quantity"), session
        )

        # Commit the transaction
        session.commit_transaction()

        return JSONResponse(
            {"msg": "payment success"},
            status_code=200,
        )
    except Exception as err:
        # Abort the transaction in case of an error
        session.abort_transaction()
        return JSONResponse({"msg": str(err)}, status_code=400)