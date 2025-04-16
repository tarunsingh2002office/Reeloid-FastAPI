from fastapi import Depends, Body, Request
from fastapi.responses import JSONResponse
from helper_function.apis_requests import get_current_user
from core.database import paidMintsBuyerCollection, client
from helper_function.addPointsToProfile import addPointsToProfile

async def paymentSuccess(request: Request
    #                      , token: str = Depends(get_current_user),body: dict = Body(
    #     example={
    #         "txnid": "12334",
    #         "mihpayid": "12334",
    #         "bank_ref_num": "12334",
    #         "mode": "12334",
    #         "net_amount_debit": "12334",
    #         "PG_TYPE": "12334",
    #         "pa_name": "12334",
    #     }
    # )
    ):
    # Extract form data
    form_data = await request.form()
    txnid = form_data.get("txnid")
    mihpayid = form_data.get("mihpayid", "")
    bank_ref_num = form_data.get("bank_ref_num", "")
    paymentMode = form_data.get("mode", "")
    netAmountDeducted = form_data.get("net_amount_debit", "")
    paymentGateway = form_data.get("PG_TYPE", "")
    paymentAggregator = form_data.get("pa_name", "")

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
                    "Deductable_Amount": netAmountDeducted,
                    "paymentSource": "Payu",
                    "paymentMode": paymentMode,
                    "bank_ref_num": bank_ref_num,
                    "netAmountDeducted": netAmountDeducted,
                    "paymentGateway": paymentGateway,
                    "paymentAggregator": paymentAggregator,
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