from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from streaming_app_backend.mongo_client import languages_collection, users_collection
from bson import ObjectId
from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from django.http import JsonResponse


@swagger_auto_schema(
    method="POST",
    operation_description="This API allows the user to select languages. The request should contain the user token in headers and an array of selected languages in the body.",
    manual_parameters=[
        openapi.Parameter(
            "token",  # The name of the header parameter
            openapi.IN_HEADER,  # Specifies that this is a header parameter
            description="User authentication token",  # Description of the token
            type=openapi.TYPE_STRING,  # Specifies that the type is a string
            required=True,  # Marks the token as required
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "selectedLanguages": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
                description="Array of selected languages ids",
            )
        },
        required=["selectedLanguages"],
    ),
    responses={
        200: openapi.Response(description="successfully saved the languages"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
    },
    tags=["User"],
)
@api_view(["POST"])
@csrf_exempt
def usersLanguaseSelection(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Invalid JSON"}, status=400)
        selectedLanguages = body.get("selectedLanguages")
        if not selectedLanguages:
            return JsonResponse({"msg": "could not get mandatory fields "}, status=400)
        userId = request.userId
        if len(selectedLanguages) == 0:
            return JsonResponse(
                {"msg": "no language is selected,please select a language first"},
                status=400,
            )
        afterRemovingWrongLanguage = []
        for languageId in selectedLanguages:
            if ObjectId.is_valid(languageId):
                validGenre = languages_collection.find_one(
                    {"_id": ObjectId(languageId)}
                )
                if validGenre:
                    afterRemovingWrongLanguage.append(languageId)
        if len(afterRemovingWrongLanguage) == 0:
            return JsonResponse(
                {"msg": "no language is selected,please select a language first"},
                status=400,
            )
        updatedData = users_collection.update_one(
            {"_id": ObjectId(userId)},
            {"$set": {"selectedLanguages": afterRemovingWrongLanguage}},
        )
        if updatedData:
            # validUser["selectedGenre"] = selectedGenre
            return JsonResponse(
                {"msg": "successfully saved the languages  ", "success": True},
                status=200,
            )
        else:
            return JsonResponse({"msg": "user is invalid"})
    else:
        return JsonResponse({"msg": "wrong method"})
