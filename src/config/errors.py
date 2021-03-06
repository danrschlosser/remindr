
import simplejson


######################################
#   Reminder responses
######################################

NO_REMINDERS_FOUND = (
    simplejson.dumps({
        'message' : 'No reminders found'
    }), 403
)

REMINDER_NOT_FOUND = (
    simplejson.dumps({
        'message' : 'Reminder not found'
    }), 403
)

######################################
#   User responses
######################################

NOT_LOGGED_IN = (
    simplejson.dumps({
        "message" : "You must be logged in"
    }), 401
)

USER_NOT_FOUND = (
    simplejson.dumps({
        "message" : 'User not found'
    }), 403
)

USER_ALREADY_EXISTS = (
    simplejson.dumps({
        "message": 'Email already used'
    }), 400
)

BAD_LOGIN = (
    simplejson.dumps({
        "message" : "Your login credentials were invalid"
    }), 401
)

ALREADY_SIGNED_IN = (
    simplejson.dumps({
    "message" : "You're already signed in"
    }), 400
)

######################################
#   General responses
######################################

NO_DATA = (
    simplejson.dumps({
        "message" : "You need to pass in data"
    }), 400
)

