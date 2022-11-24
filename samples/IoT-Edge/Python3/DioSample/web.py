from flask import Flask, request, render_template
from dioHelper import dioHelper

app = Flask(__name__)
dio = dioHelper()

@app.route('/api/v1/do/<id>', methods=['GET', 'POST'])
def do(id):
    if request.method == 'GET':
        return dio.get('out', id)
    elif request.method == 'POST':
        value = request.get_json(force=True)['value']
        return dio.set('out', id, value)

@app.route('/api/v1/di/<id>', methods=['GET'])
def di(id):
    return dio.get('in', id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
