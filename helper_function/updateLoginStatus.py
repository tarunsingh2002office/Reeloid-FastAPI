from bson import ObjectId
from datetime import datetime, timezone
from helper_function.tokenCreator import tokenCreator
from core.database import (
    users_collection,
    genre_collection,
    languages_collection,
)

def updateLoginStatus(userResponse, fcmtoken, deviceType):
    try:
        updateLoggedInStatus = users_collection.update_one(
            {"_id": userResponse["_id"]}, {"$set": {"loggedInBefore": True}}
        )
        if not updateLoggedInStatus:
            raise ValueError(
                "unable to do login right now ....please retry and if problem comes again and again then contact adminstrator "
            )
        

        if updateLoggedInStatus:
            
            token = tokenCreator({"id": str(userResponse["_id"])})
            genreList = []
            if "selectedGenre" in userResponse and userResponse["selectedGenre"]:
                for genreId in userResponse["selectedGenre"]:
                    genreData = genre_collection.find_one(
                        {"_id": ObjectId(genreId)}, {"_id": 1, "name": 1, "icon": 1}
                    )
                    genreData["_id"] = str(genreData["_id"])
                    genreList.append(genreData)
            userResponse["selectedGenre"] = genreList
            languageList = []
            
            if (
                "selectedLanguages" in userResponse
                and userResponse["selectedLanguages"]
            ):
                for languageId in userResponse["selectedLanguages"]:
                    languageData = languages_collection.find_one(
                        {"_id": ObjectId(languageId)}, {"_id": 1, "name": 1}
                    )
                    languageData["_id"] = str(languageData["_id"])
                    languageList.append(languageData)
            userResponse["selectedLanguages"] = languageList
            if not userResponse.get("Devices"):
                updatedResponse = users_collection.update_one(
                    {"_id": ObjectId(userResponse["_id"])},
                    {
                        "$set": {
                            "Devices": [
                                {
                                    "fcmtoken": fcmtoken,
                                    "deviceType": deviceType or "web",
                                    "lastUpdated": datetime.now(timezone.utc),
                                }
                            ]
                        }
                    },
                )
            else:
                userDevices = userResponse.get("Devices")
                idIsPresent = False
                
                for device in userDevices:
                    if device["fcmtoken"] == fcmtoken:
                        idIsPresent = True

                        break
                if not idIsPresent:
                    userDevices.append(
                        {
                            "fcmtoken": fcmtoken,
                            "deviceType": deviceType  or "web",
                            "lastUpdated": datetime.now(timezone.utc),
                        }
                    )
                    updatedResponse = users_collection.update_one(
                        {"_id": ObjectId(userResponse["_id"])},
                        {"$set": {"Devices": userDevices}},
                    )
                
            userResponse["Devices"] = [
                {
                    "fcmtoken": fcmtoken,
                    "deviceType": deviceType  or "web",
                    "lastUpdated": datetime.now(timezone.utc),
                }
            ]
            
            userResponse["_id"] = ""
           
            return userResponse, token
    except Exception as err:
        
        raise ValueError(str(err))
