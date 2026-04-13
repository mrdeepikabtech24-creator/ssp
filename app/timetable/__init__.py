from flask import Blueprint

timetable_bp = Blueprint('timetable', __name__, url_prefix='/timetable')

from . import routes  # noqa: F401, E402
