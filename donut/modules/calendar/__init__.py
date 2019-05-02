import flask
blueprint = flask.Blueprint(
    'calendar',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/donut/modules/calendar/static')
import donut.modules.calendar.routes
