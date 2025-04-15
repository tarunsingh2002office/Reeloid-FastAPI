from bson import ObjectId
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from core.database import sliders_collection, movies_collection
from helper_function.apis_requests import get_current_user
from helper_function.serialize_mongo_document import serialize_document

async def getSliders(request:Request, token: str = Depends(get_current_user)):
    try:
        # Query all sliders
        sliders = sliders_collection.find(
            {"visible": True},
            {"linkedMovie": 1, "schemaName": 1, "type": 1, "_id": 0, "trailerUrl": 1},
        )

        # Convert the cursor to a list of serialized dictionaries
        sliders_list = [serialize_document(slider) for slider in sliders]
        serialized_sliders = []

        for currentSlider in sliders_list:

            if "linkedMovie" in currentSlider and currentSlider["linkedMovie"]:
                # Query the linked movie using its ObjectId

                sliderData = movies_collection.find_one(
                    {"_id": ObjectId(currentSlider["linkedMovie"]),"visible": True},
                    {"name": 1, "fileLocation": 1, "trailerUrl": 1, "parts": 1,"screenType":1},
                )
                if sliderData:
                    

                    sliderData["schemaName"] = currentSlider.get("schemaName", "")
                    sliderData["type"] = currentSlider.get("type", "")
                    sliderData["trailerUrl"] = sliderData.get("trailerUrl")
                    sliderData["parts"] = sliderData.get("parts")
                    # Serialize the sliderData before appending

                    serialized_sliders.append(serialize_document(sliderData))
                # print(serialized_sliders)

        return JSONResponse({"sliders": serialized_sliders})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
