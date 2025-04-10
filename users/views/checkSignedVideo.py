import hashlib
from django.http import JsonResponse
from urllib.parse import urlparse
import time
import os


def checkSignedVideo(url):
    try:
        return url # remove this line when you want to generate a signed url i am just using this return because of some ongoing functionality testing
        url = url
        if not url:
            return
        removeDomainFromURl = urlparse(url).path
        extractNecessaryData = removeDomainFromURl.rsplit("/", 1)[0] + "/"
        print(extractNecessaryData)
        Key = "vjhje15uZQUZrWhgflzy"

        current_timestamp = int(time.time())
        print(current_timestamp)
        # Step 2: Add 60 seconds (1 minute) to the current timestamp
        next_minute_timestamp = current_timestamp + 30

        # Step 3: Convert the resulting timestamp to hexadecimal
        # hex_timestamp = hex(1735388900)[2:]
        hex_timestamp = hex(next_minute_timestamp)[2:]
        exper = "300"
        conversionStr = Key + extractNecessaryData + hex_timestamp

        signedUrl = hashlib.md5(conversionStr.encode("utf-8")).hexdigest()
        return f"{url}?t={hex_timestamp}&sign={signedUrl}"
    except Exception as err:
       
        return
        # return JsonResponse({"msg": f"{url}?t={hex_timestamp}&sign={signedUrl}"})
