from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from streaming_app_backend.mongo_client import languages_collection
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi





@swagger_auto_schema(
    method="GET",
    operation_description="This API will give all the available languages to the user for selection. We need to pass the token in the headers using the 'token' key.",
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
        200: openapi.Response(description="language fetched successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
    },
    tags=["User"],
)
@api_view(["GET"])

@csrf_exempt
def usersContentLanguageList(request):
    if request.method == "GET":
        languageArray = []
        languageList = languages_collection.find()
        
        for language in languageList:
            language['_id']=str(language['_id'])
            languageArray.append(language)
        return JsonResponse({"languageList": languageArray},status=200)
    else:
        return JsonResponse({"msg": "method not allowed"},status=500)
