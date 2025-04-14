from bson import ObjectId
from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import (
    dailyCheckInTask_collection,
    checkInPoints,
)

async def dailyCheckInTask(request: Request):
    try:
        userId = request.state.userId

        checkInTask = dailyCheckInTask_collection.find({"assignedUser": userId})
        if not checkInTask:
            return JSONResponse({"msg": "no task found"})
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

        return JSONResponse({"msg": "checkIn Called", "checkInTask": taskList})
    except Exception as err:
        return JSONResponse({"msg": err})