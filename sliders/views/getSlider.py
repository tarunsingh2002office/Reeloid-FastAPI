from bson import ObjectId
from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import sliders_collection, movies_collection

def serialize_document(doc):
    """Convert MongoDB document to a JSON serializable dictionary."""
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, list):
            # Convert ObjectIds in list fields (like 'shorts') to strings
            doc[key] = [str(v) if isinstance(v, ObjectId) else v for v in value]
    return doc


async def getSliders(request:Request):
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
