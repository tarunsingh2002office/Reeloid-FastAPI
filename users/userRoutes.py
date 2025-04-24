from fastapi import APIRouter
from users.views.createUser import createUser
from users.views.signIn import signIn
from users.views.usersGenreSelection import genreSelection
from users.views.usersLAnguageSelection import usersLanguaseSelection
from users.views.usersContentLanguageList import usersContentLanguageList
from users.views.userGenreList import genreList
from users.views.userTrendingMovies import UserTrendingVideos
from users.views.shortTrendingSection import TrailerTrendingSection
from users.views.getProfileDetails import getProfileDetails
from users.views.editProfileDetails import editProfileDetails
from users.views.serachItem import serachItem
from users.views.dailyCheckinTask import dailyCheckInTask
from users.views.collectCheciNPoints import collectCheckInPoint
from users.views.markAsBookMark import markAsBookMark
from users.views.getBookMark import getBookMark
from users.views.likeVideo import likeVideo
from users.views.getAds import getAds
from users.views.googleAuth import googleAuth
from users.views.getPackage import getPackage
from users.views.fetchWalletPoints import fetchWalletPoints
from users.views.forgotPassword import forgotPassword
from users.views.verifyOtp import verifyOtp
from users.views.updatePassword import updatePassword
from users.views.getUserMintsPurchaseHistory import getUserMintPurchaseHistory
from users.views.getContinueWatchingHistory import getUserWatchHistory
from users.views.continueWatchingHistory import continueWatchingHistorySaving
from users.views.unlikeVideo import unlikeVideo
from users.views.verifyemail import verifyEmail


user_router = APIRouter(prefix="/user", tags=["Users"])

# User routes
user_router.add_api_route("/register", createUser, methods=["POST"],summary="Create a new user")
user_router.add_api_route("/signIn", signIn, methods=["POST"])
user_router.add_api_route("/genreList", genreList, methods=["GET"])
user_router.add_api_route("/genreSelector", genreSelection, methods=["POST"])
user_router.add_api_route("/languageList", usersContentLanguageList, methods=["GET"])
user_router.add_api_route("/languageSelector", usersLanguaseSelection, methods=["POST"])
user_router.add_api_route("/trendingMovies", UserTrendingVideos, methods=["GET"])
user_router.add_api_route("/trendingTrailers", TrailerTrendingSection, methods=["GET"])
user_router.add_api_route("/getUserDetails", getProfileDetails, methods=["GET"])
user_router.add_api_route("/editUserDetails", editProfileDetails, methods=["POST"])
user_router.add_api_route("/searchItem", serachItem, methods=["GET"])
user_router.add_api_route("/checkInTask", dailyCheckInTask, methods=["GET"])
user_router.add_api_route("/collectCheckIn", collectCheckInPoint, methods=["POST"])
user_router.add_api_route("/markBookMark", markAsBookMark, methods=["POST"])
user_router.add_api_route("/getBookMark", getBookMark, methods=["GET"])
user_router.add_api_route("/likeVideo", likeVideo, methods=["POST"])
user_router.add_api_route("/getAds/{path}/{sessionType}", getAds, methods=["GET"])
user_router.add_api_route("/getPackage", getPackage, methods=["GET"])
user_router.add_api_route("/googleAuth", googleAuth, methods=["POST"])
user_router.add_api_route("/fetchWallet", fetchWalletPoints, methods=["GET"])
user_router.add_api_route("/forgotPassword", forgotPassword, methods=["POST"])
user_router.add_api_route("/verifyOtp", verifyOtp, methods=["POST"])
user_router.add_api_route("/updatePassword", updatePassword, methods=["POST"])
user_router.add_api_route("/mintsPurchaseHistory",getUserMintPurchaseHistory, methods=["GET"])
user_router.add_api_route("/continueWatching", continueWatchingHistorySaving, methods=["POST"])
user_router.add_api_route("/getContinueWatching", getUserWatchHistory, methods=["GET"])
user_router.add_api_route("/unlikeVideo", unlikeVideo, methods=["POST"])
user_router.add_api_route("/verifyEmail", verifyEmail, methods=["POST"])




# user_router.add_api_route("/register/", createUser, methods=["POST"],summary="Create a new user")
# user_router.add_api_route("/signIn/", signIn, methods=["POST"])
# user_router.add_api_route("/genreList/", genreList, methods=["GET"])
# user_router.add_api_route("/genreSelector/", genreSelection, methods=["POST"])
# user_router.add_api_route("/languageList/", usersContentLanguageList, methods=["GET"])
# user_router.add_api_route("/languageSelector/", usersLanguaseSelection, methods=["POST"])
# user_router.add_api_route("/trendingMovies/", UserTrendingVideos, methods=["GET"])
# user_router.add_api_route("/trendingTrailers/", TrailerTrendingSection, methods=["GET"])
# user_router.add_api_route("/getUserDetails/", getProfileDetails, methods=["GET"])
# user_router.add_api_route("/editUserDetails/", editProfileDetails, methods=["POST"])
# user_router.add_api_route("/searchItem/", serachItem, methods=["GET"])
# user_router.add_api_route("/checkInTask/", dailyCheckInTask, methods=["POST"])
# user_router.add_api_route("/collectCheckIn/", collectCheckInPoint, methods=["POST"])
# user_router.add_api_route("/markBookMark/", markAsBookMark, methods=["POST"])
# user_router.add_api_route("/getBookMark/", getBookMark, methods=["GET"])
# user_router.add_api_route("/likeVideo/", likeVideo, methods=["POST"])
# user_router.add_api_route("/getAds/{path}/{sessionType}/", getAds, methods=["GET"])
# user_router.add_api_route("/getPackage/", getPackage, methods=["GET"])
# user_router.add_api_route("/googleAuth/", googleAuth, methods=["POST"])
# user_router.add_api_route("/fetchWallet/", fetchWalletPoints, methods=["GET"])
# user_router.add_api_route("/forgotPassword/", forgotPassword, methods=["POST"])
# user_router.add_api_route("/verifyOtp/", verifyOtp, methods=["POST"])
# user_router.add_api_route("/updatePassword/", updatePassword, methods=["POST"])
# user_router.add_api_route("/mintsPurchaseHistory/",getUserMintPurchaseHistory, methods=["GET"])
# user_router.add_api_route("/continueWatching/", continueWatchingHistorySaving, methods=["POST"])
# user_router.add_api_route("/getContinueWatching/", getUserWatchHistory, methods=["GET"])