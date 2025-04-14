# new code for mints history plan->(
from django.http import JsonResponse
from streaming_app_backend.mongo_client import (
    users_collection,
    paidMintsBuyerCollection,
)
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method="GET",
    operation_description="This API will give user mint purchase history. We need to pass the token in the headers using the 'token' key.",
    manual_parameters=[
        openapi.Parameter(
            "token",  # The name of the header parameter
            openapi.IN_HEADER,  # Specifies that this is a header parameter
            description="User authentication token",  # Description for the header
            type=openapi.TYPE_STRING,  # Specifies that the type is a string
            required=True,  # Marks the token as required
        )
    ],
    responses={
        200: openapi.Response(description="User history fetched successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
        500: openapi.Response(description="method not allowed"),
    },
    tags=["User"],
)
@api_view(["GET"])
@csrf_exempt
def getUserMintPurchaseHistory(request):
    if request.method == "GET":
        try:
            userId = request.userId
            if not userId:
                return JsonResponse({"msg": "userId is missing"}, status=400)

            userDetails = users_collection.find_one(
                {"_id": ObjectId(userId)},
                {"password": 0},
            )
            if not userDetails:
                return JsonResponse({"msg": "no user found"}, status=400)

            userMintsPurchaseHistory = paidMintsBuyerCollection.find(
                {"userId": userId},
                {
                    "_id": 1,
                    "txnid": 1,
                    "date": 1,
                    "netAmountDeducted": 1,
                    "status": 1,
                    "quantity": 1,
                    "amount": 1,
                },
            )

            if not userMintsPurchaseHistory:
                return JsonResponse({"msg": "no purchase history found"}, status=400)

            history = []
            for planPurchaseData in userMintsPurchaseHistory:
                planPurchaseData["_id"] = str(planPurchaseData["_id"])
                history.append(planPurchaseData)

            return JsonResponse({"userMintsPurchaseHistory": history}, status=200)
        except Exception as err:
            return JsonResponse({"msg": str(err)}, status=500)

    else:
        return JsonResponse({"msg": "method not allowed"}, status=500)
