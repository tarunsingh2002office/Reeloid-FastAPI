from django.http import JsonResponse
from streaming_app_backend.mongo_client import (
    dailyCheckInTask_collection,
    checkInPoints,
)
import json
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt

from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method="POST",
    operation_description="This API allows the user to get check in task . The request should contain the user token in headers .",
    manual_parameters=[
        openapi.Parameter(
            "token",  # The name of the header parameter
            openapi.IN_HEADER,  # Specifies that this is a header parameter
            description="User authentication token",  # Description of the token
            type=openapi.TYPE_STRING,  # Specifies that the type is a string
            required=True,  # Marks the token as required
        )
    ],
    responses={
        200: openapi.Response(description="profile updated successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
        500: openapi.Response(description="method not allowed"),
    },
    tags=["User"],
)
@api_view(["POST"])
# @csrf_exempt
@csrf_exempt
def dailyCheckInTask(request):
    if request.method == "POST":
     try:
            userId = request.userId

            checkInTask = dailyCheckInTask_collection.find({"assignedUser": userId})
            if not checkInTask:
                return JsonResponse({"msg": "no task found"})
            taskList = []
            for task in checkInTask:

                checkInPointsData = checkInPoints.find_one(
                    {"_id": ObjectId(task["assignedTaskId"])}, {"_id": 0}
                )
                if checkInPointsData:

                    taskDetails = {
                        "taskId": str(task.get("_id")),
                        "status": task.get("status"),
                        "obtainable": task.get("obtainable"),
                        **checkInPointsData,
                    }
                    taskList.append(taskDetails)

            return JsonResponse({"msg": "checkIn Called", "checkInTask": taskList})
     except Exception as err:
         return JsonResponse({"msg": err})
        