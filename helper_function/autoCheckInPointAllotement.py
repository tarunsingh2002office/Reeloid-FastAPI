from core.database import (
    users_collection,
    checkInPoints,
    dailyCheckInTask_collection,
    client,
)
from celery import shared_task
from datetime import datetime, timedelta

@shared_task()
def autoCheckInPointAllotement():

    current_date = datetime.today().strftime("%d/%m/%Y")
    next_allocation_date = (datetime.today() + timedelta(days=7)).strftime("%d/%m/%Y")
    session = client.start_session()
    session.start_transaction()
    try:

        users = users_collection.find(
            {"next_Allocation": current_date}, {"_id": 1, "assignedCheckInTask": 1}
        )

        for user in users:
      
            checkInResponse = (
                checkInPoints.find({}, {"_id": 1})
                .skip(user.get("assignedCheckInTask", 0))
                .limit(7)
            )
            allotedTask = []
            for index, checkInData in enumerate(checkInResponse):
              
                new_task = {
                    "assignedTaskId": str(checkInData.get("_id")),
                    "assignedUser": str(user.get("_id")),
                    "status": "Pending" ,
                    "obtainable": (datetime.today() + timedelta(days=index)).strftime(
                        "%d/%m/%Y"
                    ),
                }
                allotedTask.append(new_task)

            if allotedTask:
                dailyCheckInTask_collection.insert_many(
                    allotedTask, session=session
                )
                users_collection.update_one(
                    {"_id": user["_id"]},
                    {
                        "$inc": {"assignedCheckInTask": 7},
                        "$set": {"next_Allocation": next_allocation_date},
                    },  # Updating next 7 days date
                    session=session,
                )

        # raise ValueError("error in nothing")
        session.commit_transaction()
        # return JsonResponse({"msg": "err"})
    except Exception as err:
        # print(err)
        session.abort_transaction()
        raise ValueError(f"Error during autoCheckInPointAllotement: {str(err)}")

    finally:
        # End session
        session.end_session()
