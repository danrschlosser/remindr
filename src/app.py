
# libraries
from flask.ext.pymongo import PyMongo
from flask import Flask, make_response, request, session, redirect
from functools import wraps
from datetime import datetime, timedelta
import simplejson

# config
from config import responses    as RESP
from config import errors       as ERR
from config import mongo_config as MONGO

# controllers
from controllers import user as user_controller
from controllers import reminder as reminder_controller
from controllers import forwarders as forwarders_controller
from controllers import oauth as oauth_controller

# dropbox oauth
import dropbox
from os import environ
DROPBOX_API_KEY = environ['DROPBOX_API_KEY']
DROPBOX_SECRET = environ['DROPBOX_SECRET']
flow = dropbox.client.DropboxOAuth2FlowNoRedirect(DROPBOX_API_KEY, DROPBOX_SECRET)


app = Flask(__name__)
app.config.from_object('config.flask_config')
mongo = PyMongo(app)


##############################################################################
#   ROUTE WRAPPERS
##############################################################################

# user must be logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return ERR.NOT_LOGGED_IN
        return f(*args, **kwargs)
    return decorated_function


# user cannot be logged in
def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            return ERR.ALREADY_SIGNED_IN
        return f(*args, **kwargs)
    return decorated_function


##############################################################################
#   user
##############################################################################

@app.route('/user/<identifier>', methods=['GET'])
def get_user(identifier):
    return user_controller.get_user(mongo, uid=identifier, data={'return': ['username']})


@app.route('/user/list', methods=['GET'])
def user_list():
    return user_controller.get_users(mongo)

    
##############################################################################
#   reminder
##############################################################################

@app.route('/reminder/create', methods=['POST'])
def create_reminder():
    return reminder_controller.create(mongo, data=simplejson.loads(request.data))


@app.route('/reminder/complete/<rid>', methods=['POST'])
def complete_reminder(rid):
    return reminder_controller.complete(mongo, data={"rid": rid})


@login_required
@app.route('/reminder/list', methods=['GET'])
def list_reminders():
    return reminder_controller.list(mongo)


##############################################################################
#   Forwarders
##############################################################################

@login_required
@app.route('/forwarders/update', methods=['POST'])
def update_forwarders():
    return forwarders_controller.update(mongo, data=simplejson.loads(request.data))


@login_required
@app.route('/forwarders', methods=['GET'])
def get_forwarders():
    return forwarders_controller.find_by_current_user(mongo)

##############################################################################
#   authentication
##############################################################################

@app.route('/login', methods=['POST'])
def login():
    return user_controller.login(mongo, data=simplejson.loads(request.data))


@app.route('/signup', methods=['POST'])
def signup():
    return user_controller.signup(mongo, data=simplejson.loads(request.data))


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    return user_controller.logout()

##############################################################################
#   OAuth
##############################################################################

@app.route('/connect/dropbox')
@login_required
def connect_to_dropbox():
    authorize_url = flow.start() + '&redirect_uri=http://localhost:5000/#/configure'
    return redirect(authorize_url)


def receive_dropbox_token():
    code = request.args.get('code')
    access_token, user_id = flow.finish(code)
    oauth_controller.save_dropbox(mongo, access_token)


##############################################################################
#   main
##############################################################################

@app.route('/reminder/defaults', methods=['GET'])
def get_reminder_defaults():
    today = datetime.now()
    return simplejson.dumps({
        'date_str' : (today + timedelta(days=1)).strftime(MONGO.DATEPICKER_FORMAT) + ' 00:00',
        'time_str' : today.strftime('%H:%M')
    }), 200


# returns json w/ unique identifier
@app.route('/session')
def get_session():
    if 'username' in session:
        return simplejson.dumps({
            'username'  : session['username'],
            'email'     : session['email'],
            'id'       : session['uid']
        }), 200
    return ERR.NOT_LOGGED_IN


# logout endpoint. clears the session
@app.route('/logout', methods=['POST'])
@login_required
def log_out():
    session.clear()
    return 'Logged out', 200


@app.route('/', methods=['GET'])
def home():
    return make_response(open('src/static/base.html').read())


if __name__ == '__main__':
    app.run()
