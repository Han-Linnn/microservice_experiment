
from flask import g, request, Flask, jsonify, abort
import jwt
from jwt import exceptions
import datetime


### ENTRYPOINT ###
# Setup the application as a Flask app
app = Flask(__name__)


# In-memory of the user information
users_dict = {}

# ID of the user information
identificator = 0

headers = {
    'typ': 'jwt',
    'alg': 'HS256'
}

# Use Salt to hash token
SALT = 'iv%i6xo7l8_t9bf_u!8#g#m*)*+ej@bek6)(@u3kh*42+unjv='


def create_token(username, password):
    # generate payload
    payload = {
        'username': username,
        'password': password,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # expire time
    }
    result = jwt.encode(payload=payload, key=SALT, algorithm="HS256", headers=headers)
    return result


### API FUNCTIONS ###
# Create a new user and store in memory
@app.route("/users", methods=['GET', 'POST', 'PUT'])
def generate_users():

    if request.method == "GET":
        return "/ GET", 200

    elif request.method == "POST":

        global identificator

        user = {}
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            user['username'] = username
            user['password'] = password
            user['user_list'] = []
            users_dict[identificator] = user
            identificator += 1
            return {"code": 200, "message": "success", "data": users_dict}, 200
        else:
            return {'code': 401, 'message': 'Username or Password is empty.'}, 401


# login
@app.route('/users/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get("username")
        password = data.get("password")
        for get_user in users_dict.values():
            # Verify whether the username and password exist, if it is true, generate a token and save it in memory
            if get_user['username'] == username and get_user['password'] == password:
                token = create_token(username, password)
                get_user['token'] = token
                return {"code": 200, "message": "success", "data": get_user}
            else:
                continue

        return "User is not exist.", 403

    elif request.method == 'GET':
        return {"code": 202, "message": "get is nothing"}
    else:
        return {"code": 203, "message": "'not support other method'"}


@app.route('/auth', methods=['GET'])
def verify_jwt():
    # verify token
    auth = request.headers.get('Authentication')
    if auth:
        g.username = None
        try:
            "extract the payload information"
            payload = jwt.decode(auth, SALT, algorithms=['HS256'])
            "assign it to the Object g to save"
            username = payload.get('username')
            password = payload.get('password')
            for check_user in users_dict.values():
                # Verify whether the username and password exist, if it is true, generate a token and save it in memory
                if check_user['username'] == username and check_user['password'] == password:
                    return jsonify({'message': check_user['username']})
                else:
                    continue
            return "illegal token", 403

        except exceptions.ExpiredSignatureError:  # 'token is already invalid'
            return jsonify({'message': 1})
        except jwt.DecodeError:  # 'fail to verify token'
            return jsonify({'message': 2})
        except jwt.InvalidTokenError:  # 'illegal token'
            return jsonify({'message': 3})


@app.route('/url', methods=['POST'])
def url_match_user():
    data = request.form['url_id']
    username = request.form['username']
    for current_user in users_dict.values():
        # Verify whether the username and password exist, if it is true, generate a token and save it in memory
        if current_user['username'] == username:
            current_user['user_list'].append(data)
            return jsonify({'message': 'success'})
        else:
            continue
    return jsonify({'message': 'error'})


@app.route('/verify_user', methods=['POST'])
def verify_user():
    data = request.form['url_id']
    username = request.form['username']
    for current_user in users_dict.values():
        # Verify whether the username and password exist, if it is true, generate a token and save it in memory
        if current_user['username'] == username:
            if data in current_user['user_list']:
                return jsonify({'message': 'success'})
            else:
                return jsonify({'message': 'error1'})
        else:
            continue
    return jsonify({'message': 'error2'})


@app.route('/current_user_url', methods=['POST'])
def get_current_user_url():
    username = request.form['username']
    for current_user in users_dict.values():
        if current_user['username'] == username:
            url_list = current_user['user_list']
            return jsonify({'message': url_list})
        else:
            continue
    return jsonify({'message': 'error'})