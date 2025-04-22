from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from core.config import db_settings

# Create a MongoDB client
client = MongoClient(db_settings.MONGODB_URI)

# Access the default database
db = client.get_database("testing")  # This uses the default database from the URI

# Define collections
sliders_collection = db.sliders
movies_collection = db.movies
shorts_collection = db.shorts
layouts_collection = db.layouts
users_collection = db.users
genre_collection = db.genres
languages_collection = db.languages
dailyCheckInTask_collection = db.dailycheckintasks
checkInPoints = db.checkinpoints
adsCollection = db.ads
paidMintsBuyerCollection = db.paidMintsBuyer
mintsPlanCollection = db.mintsplans
videoPurchasedLogs = db.videoPurchasedLogs
userReactionLogs = db.userReactionLogs
forgotPasswordRequests = db.forgotPasswordRequests
continueWatching = db.continueWatching
verificationCode = db.verificationCode