import json
from bson import ObjectId
from fastapi import Depends, Request, Body
from datetime import datetime
from fastapi.responses import JSONResponse
from core.database import (
    dailyCheckInTask_collection,
    checkInPoints,
    client,
)
from helper_function.addPointsToProfile import addPointsToProfile
from helper_function.apis_requests import get_current_user

async def collectCheckInPoint(request:Request,
                              token: str = Depends(get_current_user)
                              ,body: dict = Body(
        example={
            "taskId": "1234"
        }
    )):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON format"}, status_code=400)
    session = None
    try:
        taskId = body.get("taskId")
        userId = request.state.userId

        if not taskId:
            return JSONResponse({"msg": "No Task Id Is present"}, status_code=404)
        if not userId:
            return JSONResponse({"msg": "Invalid user "}, status_code=404)
        # Try to update the task status to "Completed"
        current_date_str = datetime.today().strftime("%d/%m/%Y")
        taskPresent = await dailyCheckInTask_collection.find_one(
            {
                "_id": ObjectId(taskId),
                "assignedUser": userId,
                "status": "Pending",
            }
        )
        if not taskPresent:
            return JSONResponse({"msg": "Task not found"}, status_code=404)
        session = await client.start_session()
        session.start_transaction()

        obtainable_str = taskPresent.get("obtainable")  # e.g., "31/01/2025"
        # current_date_str = "01/02/2025"  # Example current date

        # Convert to datetime objects
        obtainable = datetime.strptime(obtainable_str, "%d/%m/%Y")
        current_date = datetime.strptime(current_date_str, "%d/%m/%Y")

        if current_date >= obtainable:
            taskIsPresent = await dailyCheckInTask_collection.find_one_and_update(
                {
                    "_id": ObjectId(taskId),
                    "assignedUser": userId,
                    "status": "Pending",
                },
                {"$set": {"status": "Completed"}},
                session=session,
            )
            # print(taskIsPresent)
            if taskIsPresent:

                taskPoints = await checkInPoints.find_one(
                    {"_id": ObjectId(taskIsPresent.get("assignedTaskId"))},
                    {"allocatedPoints": 1},
                    session=session,
                )

                if taskPoints:
                    await addPointsToProfile(
                        userId, taskPoints.get("allocatedPoints"), session
                    )
                    session.commit_transaction()
                    return JSONResponse(
                        {
                            "msg": "Task completed successfully",
                            "allocatedPoints": taskPoints.get("allocatedPoints"),
                        },
                        status_code=200,
                    )
                else:

                    return JSONResponse(
                        {"msg": "Points data not found for this task"}, status_code=404
                    )

            else:

                return JSONResponse(
                    {"msg": "No task found or task already completed"}, status_code=404
                )

        else:

            return JSONResponse(
                {
                    "msg": "You can not collect upcoming Task Points before its obtainable date"
                },
                status_code=400,
            )
    except Exception as err:
        return JSONResponse({"msg": str(err)}, status_code=400)
    finally:
        if session:
            session.end_session()
