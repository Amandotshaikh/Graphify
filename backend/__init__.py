from flask import Blueprint

backend = Blueprint("backend", __name__)

from .auth import auth
from .database import init_db


