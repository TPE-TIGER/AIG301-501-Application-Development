from flask import Flask, request, render_template, redirect, url_for
from tpmHelper import tpmHelper
import os, json

app = Flask(__name__)
credential_path = './data/credentials'
tpm_helper = None
credentials = None

def init():
    global tpm_helper
    os.makedirs('./data', exist_ok = True)
    tpm_helper = tpmHelper()
    load_credentials()

def load_credentials():
    global credential_path, credentials
    credentials = {}
    if os.path.exists(credential_path):
        credentials_string = tpm_helper.decrypt('', credential_path, False)
        if credentials_string:
            credentials = json.loads(credentials_string)

@app.route('/')
def index():
    global credentials
    return render_template('login.html', data=list(credentials.keys()))

@app.route('/login', methods=['GET', 'POST'])
def login():
    global credentials
    error = None
    if request.method == 'POST':
        if not request.form['username'] in credentials or request.form['password'] != credentials[request.form['username']]:
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error, data=list(credentials.keys()))

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    global credential_path, credentials, tpm_helper
    error = None
    if request.method == 'GET':
        return render_template('manage.html', data=list(credentials.keys()))
    elif request.method == 'POST':
        if request.form['username'] in credentials:
            error = 'User already exists.'
            return render_template('login.html', error=error, data=list(credentials.keys()))
        else:
            credentials[request.form['username']] = request.form['password']
            tpm_helper.encrypt(credential_path, json.dumps(credentials), False)
            return redirect(url_for('login'))

@app.route('/delete', methods=['POST'])
def delete():
    global credential_path, credentials, tpm_helper
    print('DELETE - ' + str(request.form))
    credentials.pop(request.form['username'], False)
    tpm_helper.encrypt(credential_path, json.dumps(credentials), False)
    return redirect(url_for('login'))

@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

if __name__ == '__main__':
    init()
    app.run(host='0.0.0.0', port=443, debug=True)
