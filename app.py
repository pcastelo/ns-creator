import logging
import os
import subprocess
# import json
import toml

from flask import Flask, render_template, request

from exception.LoginException import LoginException

app = Flask(__name__)
logging.basicConfig(level=logging.ERROR)


@app.route('/')
def index():
    return render_template('index.html')


# this is then route that receive the user and password for call later flyctl
@app.route('/create', methods=['POST'])
def create():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    ns_password = request.form['ns_password']
    mongodb_url = request.form['mongodb_url']


    try:
        access_token = login(email, password)
    except LoginException as e:
        return render_template('index.html', error=e.message)

    createOrg(access_token)
    modifyTomlFile(mongodb_url, ns_password, username)

    return launchApp(access_token, username)


def createOrg(access_token):
    # create new organization in fly.io with flyctl
    create_org_result = subprocess.getoutput('flyctl orgs create personal -j -t {}'.format(access_token))
    app.logger.info('resultado: %s', create_org_result)


def launchApp(access_token, username):
    # Deploy the app to fly.io

    # TODO revisar esto o se jode si tiene o no cuentas creadas
    # checks apps list before create a new one in json format and parse it
    # apps_list = json.loads(subprocess.getoutput('flyctl apps list -j'))
    # app.logger.info(apps_list)
    # if (len(apps_list) > 0):
    #     app.logger.info('app already created')
    #     return render_template('index.html', error='App already created')
    # else:

    # launch new app with nightscout image
    app.logger.info('Launching new app')
    app_status = subprocess.getoutput(
        'flyctl launch --org personal --name {} --region mia --image nightscout/cgm-remote-monitor:latest --now  --path /tmp/{} --copy-config -t {}'
        .format(username, username, access_token))
    app.logger.info('app_status: %s', app_status)
    os.system('rm -rf /tmp/{}'.format(username))

    return render_template('index.html', ok='App create successfully')


def modifyTomlFile(mongodb_url, ns_password, username):
    # Modify environment variables from fly.toml
    app.logger.info('Modifying toml file')
    data = toml.load("/tmp/base/fly.toml")
    data['env']['API_SECRET'] = ns_password
    data['env']['MONGODB_URI'] = mongodb_url
    userpath = '/tmp/{}/fly.toml'.format(username)
    # create a directory for the user
    app.logger.info('Creating directory for user')
    os.makedirs(os.path.dirname(userpath), exist_ok=True)
    f = open(userpath, 'w')
    toml.dump(data, f)
    f.close()
    app.logger.info('toml file modified')


# Login to flyctl and validate the user and password and get the access token
def login(email, password):
    login_result = subprocess.getoutput('flyctl auth login --email {} --password {} --otp none'.format(email, password))
    # if error show in index.html error message else get acccess token
    app.logger.info('resultado: %s', login_result)
    if 'Incorrect email and password' in login_result:
        app.logger.error('Incorrect Credentials')
        raise LoginException("Incorrect Credentials")
    else:
        access_token = subprocess.getoutput('flyctl auth token')
        os.system('flyctl auth logout')
    return access_token


if __name__ == '__main__':
    app.run(port=5000)
