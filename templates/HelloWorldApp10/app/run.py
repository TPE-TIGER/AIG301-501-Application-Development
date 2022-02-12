# -*- coding: utf-8 -*-
from flask import Flask 

app = Flask(__name__)

#Define Flask Key
app.secret_key = 'my secret key'

# --------------------------------------------------------- #

#get /api/v1/hello-world
@app.route('/api/v1/hello-world', methods=['GET'])
def hello_world():
    return 'Hello World.'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
