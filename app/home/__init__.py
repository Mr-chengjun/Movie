from flask import Blueprint

home = Blueprint("home", __name__)


# import app.home.views  # 1
from . import views  # 与1等效
from . import verify_code
