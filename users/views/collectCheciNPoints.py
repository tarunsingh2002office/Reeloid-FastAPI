import json
from bson import ObjectId
from datetime import datetime
from fastapi import Depends, Request, Body
from fastapi.responses import JSONResponse
from core.database import (
    dailyCheckInTask_collection,
    users_collection,
    checkInPoints,
    client,
)
from helper_function.apis_requests import get_current_user

async def collectCheckInPoint(
    request: Request,
    token: str = Depends(get_current_user),
    body: dict = Body(
        example={
            "taskId": "1234"
        }
    )
):
    try:
        body = await request.json()
        taskId = body.get("taskId")
        userId = request.state.userId

        if not taskId:
            return JSONResponse({"msg": "No Task Id Is present"}, status_code=404)
        if not userId:
            return JSONResponse({"msg": "Invalid user"}, status_code=404)

        taskPresent = await dailyCheckInTask_collection.find_one(
            {
                "_id": ObjectId(taskId),
                "assignedUser": userId,
                "status": "Pending",
            }
        )
        if not taskPresent:
            return JSONResponse({"msg": "Task not found"}, status_code=404)
        
        current_date_str = datetime.today().strftime("%d/%m/%Y")
        obtainable_str = taskPresent.get("obtainable")
        obtainable = datetime.strptime(obtainable_str, "%d/%m/%Y")
        current_date = datetime.strptime(current_date_str, "%d/%m/%Y")

        if current_date < obtainable:
            return JSONResponse(
                {"msg": "You cannot collect upcoming Task Points before its obtainable date"},
                status_code=400,
            )
        
        taskPoints = await checkInPoints.find_one(
                    {"_id": ObjectId(taskPresent.get("assignedTaskId"))},
                    {"allocatedPoints": 1},
                )
        
        if not taskPoints:
            return JSONResponse(
                {"msg": "Points data not found for this task"},
                status_code=404,
            )
        
        allotedPoints = taskPoints.get("allocatedPoints")

        async with await client.start_session() as session:
            async def txn(sess):
                taskIsPresent = await dailyCheckInTask_collection.find_one_and_update(
                    {
                        "_id": ObjectId(taskId),
                        "assignedUser": userId,
                        "status": "Pending",
                    },
                    {"$set": {"status": "Completed"}},
                    session=sess,
                )
                if not taskIsPresent:
                    raise Exception("Not able to change the status of the task")  
                
                updateUser = await users_collection.update_one(
                        {"_id": ObjectId(userId)}, 
                        {
                            "$inc": {"allocatedPoints": int(allotedPoints)}
                        },  
                        upsert=True,  
                        session=sess,
                    )

                if updateUser.acknowledged and updateUser.modified_count > 0:
                    return {"success": True, "data": updateUser.raw_result}
                else:
                    raise ValueError("Failed to update points.")

            try:
                await session.with_transaction(txn)
            except Exception as err:
                return JSONResponse({"msg": f"Unexpected error: {str(err)}"}, status_code=500)
        return JSONResponse(
            {
                "msg": "Task completed successfully",
                "allocatedPoints": allotedPoints,
            },
            status_code=200,
        )
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON format"}, status_code=400)
    except Exception as err:
        return JSONResponse({"msg": f"Unexpected error: {str(err)}"}, status_code=500)