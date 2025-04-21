import json
import asyncio
from bson import ObjectId
from datetime import datetime
from fastapi import Depends, Request, Body
from fastapi.responses import JSONResponse
from core.database import (
    dailyCheckInTask_collection,
    checkInPoints,
    client,
)
from helper_function.apis_requests import get_current_user
from helper_function.addPointsToProfile import addPointsToProfile

async def collectCheckInPoint(
    request: Request,
    token: str = Depends(get_current_user),
    body: dict = Body(
        example={
            "taskId": "1234"
        }
    )
):
    max_retries = 3  
    try:
        body = await request.json()
        taskId = body.get("taskId")
        userId = request.state.userId

        if not taskId:
            return JSONResponse({"msg": "No Task Id Is present"}, status_code=404)
        if not userId:
            return JSONResponse({"msg": "Invalid user"}, status_code=404)

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

        obtainable_str = taskPresent.get("obtainable")
        obtainable = datetime.strptime(obtainable_str, "%d/%m/%Y")
        current_date = datetime.strptime(current_date_str, "%d/%m/%Y")

        if current_date < obtainable:
            return JSONResponse(
                {"msg": "You cannot collect upcoming Task Points before its obtainable date"},
                status_code=400,
            )

        for attempt in range(max_retries):
            session = await client.start_session()
            session.start_transaction()
            try:
                taskIsPresent = await dailyCheckInTask_collection.find_one_and_update(
                    {
                        "_id": ObjectId(taskId),
                        "assignedUser": userId,
                        "status": "Pending",
                    },
                    {"$set": {"status": "Completed"}},
                    session=session,
                )
                if not taskIsPresent:
                    session.abort_transaction()
                    return JSONResponse(
                        {"msg": "No task found or task already completed"},
                        status_code=404,
                    )

                taskPoints = await checkInPoints.find_one(
                    {"_id": ObjectId(taskIsPresent.get("assignedTaskId"))},
                    {"allocatedPoints": 1},
                    session=session,
                )
                if not taskPoints:
                    session.abort_transaction()
                    return JSONResponse(
                        {"msg": "Points data not found for this task"},
                        status_code=404,
                    )

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
            except Exception as err:
                if session and session.in_transaction:
                    session.abort_transaction()
                if "TransientTransactionError" in str(err) and attempt < max_retries - 1:
                    await asyncio.sleep(0.1)  # Small delay before retrying
                    continue
                return JSONResponse({"msg": f"Error: {str(err)}"}, status_code=500)
            finally:
                session.end_session()
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON format"}, status_code=400)
    except Exception as err:
        return JSONResponse({"msg": f"Unexpected error: {str(err)}"}, status_code=500)