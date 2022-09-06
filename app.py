import logging
import os
import subprocess
import json
import toml

from flask import Flask, render_template, request

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


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

    # Login to flyctl and validate the user and password
    login_result = subprocess.getoutput('flyctl auth login --email {} --password {} --otp none'.format(email, password))
    # if error show in index.html error message
    app.logger.info('resultado: %s', login_result)
    if ('Incorrect email and password' in login_result):
        app.logger.info('Incorrect Credentials')
        return render_template('index.html', error='Incorrect credentials')
    # create new organization in fly.io with flyctl
    createOrgResult = subprocess.getoutput('flyctl orgs create personal -j')
    app.logger.info('resultado: %s', createOrgResult)

    # Modify environment variables from fly.toml
    data = toml.load("/tmp/base/fly.toml")
    data['env']['API_SECRET'] = ns_password
    data['env']['MONGODB_URI'] = mongodb_url
    # Generic item from example you posted
    # To use the dump function, you need to open the file in 'write' mode
    # It did not work if I just specify file location like in load
    userpath = '/tmp/{}/fly.toml'.format(username)
    # create a directory for the user
    os.makedirs(os.path.dirname(userpath), exist_ok=True)
    f = open(userpath, 'w')
    toml.dump(data, f)
    f.close()

    # TODO revisar esto o se jode si tiene o no cuentas creadas
    # Deploy the app to fly.io
    # checks apps list before create a new one in json format and parse it
    # apps_list = json.loads(subprocess.getoutput('flyctl apps list -j'))
    # app.logger.info(apps_list)
    # if (len(apps_list) > 0):
    #     app.logger.info('app already created')
    #     return render_template('index.html', error='App already created')
    # else:
    # launch new app with nightscout image
    app.logger.info('launching new app')
    app_status = subprocess.getoutput(
        'flyctl launch --org personal --name {} --region mia --image nightscout/cgm-remote-monitor:latest --now  --path /tmp/base --copy-config'.format(
            username))
    app.logger.info('app_status: %s', app_status)
    os.system('flyctl auth logout')
    return render_template('index.html', ok='App create successfully')

if __name__ == '__main__':
    app.run()
