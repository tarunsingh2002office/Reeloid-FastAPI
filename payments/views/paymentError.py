from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from streaming_app_backend.mongo_client import paidMintsBuyerCollection
import os


@csrf_exempt
def paymentError(request):

    PAYU_KEY = os.getenv("PAYU_KEY")
    PAYU_SALT = os.getenv("PAYU_SALT")
    txnid = request.POST.get("txnid")
    headers = {"key": PAYU_KEY, "command": "verify_payment"}
    mihpayid = request.POST.get("mihpayid") or ""
    bank_ref_num = request.POST.get("bank_ref_num") or ""

    paymentMode = request.POST.get("mode") or ""

    netAmountDeducted = request.POST.get("net_amount_debit") or ""
    paymentGateway = request.POST.get("PG_TYPE") or ""
    paymentAggregator = request.POST.get("pa_name") or ""
    error_message = request.POST.get("error_Message", "Payment Failed")
    try:

        # reqData = requests.post("https://test.payu.in/merchant/postservice.php?form=2")
        # print(reqData)
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

        return JsonResponse(
            {"msg": "payment Failed", "txnid": txnid, "error_message": error_message},
            status=200,
        )
    except Exception as err:
        # session.abort_transaction()
        return JsonResponse({"msg": str(err)}, status=400)
