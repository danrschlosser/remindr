
import requests
import simplejson
import base64

BASE_URL = 'https://api.github.com'
REPO_NAME = 'TODO_LIST'


def get_repo(TOKEN):
    headers = {
        'Authorization' : 'token ' + TOKEN
    }
    resp = simplejson.loads(requests.get(
        BASE_URL+'/user/repos',
        headers = headers
    ).text)
    #for x in resp:
    #   print x
    names = [repo['name'] for repo in resp]

    if REPO_NAME not in names:
        USERNAME = get_username(TOKEN)
        return make_repo(TOKEN, USERNAME)
    return


def make_repo(TOKEN, USERNAME):

    # making the repo
    headers = {
        'Authorization' : 'token ' + TOKEN
    }
    params = {
        'name'  : REPO_NAME,
        'description'   : ('Generated by Remindr to create github issues for '+
            USERNAME +' so they finish their TODO list'),
        'auto_init' : True
    }
    resp = requests.post(
        BASE_URL+'/user/repos',
        headers = headers,
        data = simplejson.dumps(params)
    )

    if resp.status_code != 201:
        print resp.text
        return simplejson({
            'message' : "Our github integration broke :("
        }), 400

    # getting the README
    resp = requests.get(
        BASE_URL + '/repos/'+USERNAME+'/'+REPO_NAME+'/readme',
        headers = headers
    )
    README = simplejson.loads(resp.text)

    # updating the README
    params = {
        'path'      : 'README.md',
        'message'   : 'adding README explanation',
        'content'   : base64.b64encode('#TODO LIST\n\nThis is an autogenerated' +
            ' repo by Remindr to make github issue reminders for u/'+USERNAME),
        'sha'       : README['sha']
    }
    resp = requests.put(
        BASE_URL + '/repos/'+USERNAME+'/'+REPO_NAME+'/contents/README.md',
        headers = headers,
        data = simplejson.dumps(params)
    )
    if resp.status_code != 200:
        print resp.text
        return simplejson({
            'message' : "Our github integration broke :("
        }), 400


def get_username(TOKEN):
    headers = {
        'Authorization' : 'token ' + TOKEN
    }
    resp = requests.get(
        BASE_URL + '/user',
        headers = headers
    )
    user = simplejson.loads(resp.text)
    return user['login']


def create_issue(TOKEN, USERNAME, reminder):
    headers = {
        'Authorization' : 'token ' + TOKEN
    }

    data = {
        'title' : reminder['task'],
        'body'  : reminder['details'],
        'assignee'  : USERNAME
    }

    resp = requests.post(
        BASE_URL+'/repos/'+USERNAME+'/'+REPO_NAME+'/issues',
        data = simplejson.dumps(data),
        headers = headers
    )

    if resp.status_code == 201:
        print 'SUCCESS'
    else:
        print 'OOPS'


def run(reminder, forwarders, user=None):

    TOKEN = forwarders['forwarders']['github']['token']
    USERNAME = get_username(TOKEN)
    get_repo(TOKEN, USERNAME)
    create_issue(TOKEN, USERNAME, reminder) 
