from fastapi import APIRouter
from sliders.views.getSlider import getSliders
from sliders.views.getMovieData import getMovieData
from sliders.views.getLayouts import getLayouts
from sliders.views.getDataRelatedToLayouts import getDataRelatedToLayOuts
from sliders.views.refreshTheVideoURL import refreshTheVideoURL
from sliders.views.purchasePremiumVideo import purchasePremiumVideo

slider_router = APIRouter(prefix="", tags=["Sliders"])

# Slider routes
slider_router.add_api_route("/getSliders", getSliders, methods=["GET"])
slider_router.add_api_route("/getMovieData", getMovieData, methods=["POST"])
slider_router.add_api_route("/getLayouts", getLayouts, methods=["GET"])
slider_router.add_api_route("/getLayoutData/<layoutID>", getDataRelatedToLayOuts, methods=["GET"])
slider_router.add_api_route("/purchaseVideo",purchasePremiumVideo, methods=["POST"])
slider_router.add_api_route("/rfVid",refreshTheVideoURL, methods=["POST"])