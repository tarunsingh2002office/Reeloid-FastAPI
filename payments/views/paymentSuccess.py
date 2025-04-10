from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from streaming_app_backend.mongo_client import paidMintsBuyerCollection, client
from users.views.addPointsToProfile import addPointsToProfile
import os


@csrf_exempt
def paymentSuccess(request):
    if request.method == "POST":
        

        txnid = request.POST.get("txnid")

        mihpayid = request.POST.get("mihpayid") or ""
        bank_ref_num = request.POST.get("bank_ref_num") or ""

        paymentMode = request.POST.get("mode") or ""

        netAmountDeducted = request.POST.get("net_amount_debit") or ""
        paymentGateway = request.POST.get("PG_TYPE") or ""
        paymentAggregator = request.POST.get("pa_name") or ""

        try:
            session = client.start_session()
            session.start_transaction()
           
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

            addPointsToProfile(
                paidMintsPlan.get("userId"), paidMintsPlan.get("quantity"), session
            )

            session.commit_transaction()
            return JsonResponse(
                {
                    "msg": "payment success",
                },
                status=200,
            )
        except Exception as err:
            print(err)
            session.abort_transaction()
            return JsonResponse({"msg": str(err)}, status=400)
