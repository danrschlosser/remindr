

from flask import session
from flask.ext.pymongo import ObjectId
from functools import wraps
from datetime import datetime
import simplejson

import user as user_controller

from sys import path
path.append('../')
from config import responses as RESP
from config import errors as ERR
from config import mongo_config as MONGO
from external_task_creators import twilio_forwarder
from external_task_creators import dropbox_forwarder
from external_task_creators import email_forwarder


##############################################################################
#   Wrappers
##############################################################################

def needs_data(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'data' not in kwargs or not kwargs['data']:
            return ERR.NO_DATA
        return f(*args, **kwargs)
    return decorated_function


##############################################################################
#   controller methods
##############################################################################

@needs_data
def create(mongo, data=None):
    data = form_to_dict(data)
    if not user_controller.user_exists(mongo, {'username': data['user']}):
        return ERR.USER_NOT_FOUND

    mongo.db[MONGO.REMINDERS].insert(data)

    return RESP.REMINDER_CREATED


@needs_data
def edit(mongo, data=None):
    # TODO
    pass


@needs_data
def complete(mongo, data=None):
    print data
    response = mongo.db[MONGO.REMINDERS].update(
        {'_id' : ObjectId(data['rid'])},
        {'$set': {
            'completed' : True
        }})
    if not response:
        return ERR.REMINDER_NOT_FOUND

    return RESP.REMINDER_COMPLETED


def list(mongo):
    cursor = mongo.db[MONGO.REMINDERS].find({
        'user'     : session['username'],
        'completed' : False
    })
    reminders = [mongo_to_dict(item) for item in cursor]
    reminders = [time_to_epoch(item) for item in reminders]


    if len(reminders) == 0:
        return ERR.NO_REMINDERS_FOUND

    return simplejson.dumps({
        'reminders': reminders
    }), 200


##############################################################################
#   utility methods
##############################################################################

def time_to_epoch(data):
    epoch = datetime.utcfromtimestamp(0)
    for key in data:
        if key in ['creationDate', 'due']:
            delta = datetime.strptime(data[key], MONGO.DATETIME_FORMAT) - epoch
            # except (ValueError):
            #     delta = datetime.strptime(data[key], '%d-%B %H:%M') - epoch
            data[key] = delta.total_seconds()
            
    return data


def form_to_dict(data):
    dict = {}
    try:
        dict['creationDate'] = datetime.now().strftime(MONGO.DATETIME_FORMAT)
    except (ValueError):
        dict['creationDate'] = datetime.now().strftime('%d-%B %H:%M')

    dict['completed'] = False

    for key in data:
        print key, data[key]

    # JANKY AS COULD BE, SORRY NOT SORRY
    reminder_time = {}
    reminder_time['dueDate'] = data['dueDate'][0:10]
    reminder_time['dueTime'] = data['dueTime'].encode('utf-8')
    dict['due'] = reminder_time['dueDate'] + ' ' + reminder_time['dueTime']

    for key in ['task', 'details', 'user', 'priority']:
        if key in data:
            dict[key] = data[key]

    return dict


def mongo_to_dict(data):
    dict = {}
    for key in data:

        if key == '_id':
            dict[key] = str(data[key])
        elif key in ['completed']:
            dict[key] = data[key]
        elif 'date' in key.lower():
            dict[key] = data[key].encode('utf-8')
        elif key in ['priority']:
            pass
        else:
            dict[key] = data[key].encode('utf-8')

    return dict
