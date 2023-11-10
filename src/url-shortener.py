#!/bin/env python3

# URL SHORTENER.py
#   by Tim Müller
#
# Created:
#   03 Mar 2022, 14:25:23
# Last edited:
#   13 Apr 2022, 11:12:15
# Auto updated?
#   Yes
#
# Description:
#   Implements a barebone framework to implement the URL-shortener part of
#   assignment 2 in.
#   Build with the Flask (https://flask.palletsprojects.com/en/2.0.x/)
#   framework.
#
#   We only provide the bare flask skeleton with a couple of code paths like
#   you would find in a fully-fledged service.
#   You should only use this framework if you have no (working) implementation
#   of assignment 1, since it is obviously not a real URL-shortener.
#

from flask import g, request, Flask, current_app, jsonify, abort, redirect
import jwt
from jwt import exceptions
import functools
import datetime
import re
import requests


### ENTRYPOINT ###
# Setup the application as a Flask app
app = Flask(__name__)


### CONSTANTS ###
# Regular expression that is used to check URLs for correctness.
# Taken from: https://gist.github.com/gruber/8891611
URL_CORRECTNESS_REGEX = r"(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"

# Defines the valid characters for an identifier.
# The size of this array is used as the base for the decoding algorithm.
ALLOWED_ID_CHARACTERS = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    '_', '-'
]


### GLOBAL VALUES ###
# Keeps track of the next numeric identifier
next_id = 0

# In-memory database of the URLs we have shortened
id_url_map = {}


# Check the login state
def login_required(f):
    """Use the wraps of the functools module to decorate inner functions"""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            if g.username == 1:
                return {'code': 403, 'message': 'Token is already invalid!'}, 403
            elif g.username == 2:
                return {'code': 403, 'message': 'Fail to verify token'}, 403
            elif g.username == 3:
                return {'code': 400, 'message': 'illegal token'}, 400
            else:
                return f(*args, **kwargs)
        except BaseException as e:
            return {'code': 401, 'message': 'Please login first.'}, 401

    return wrapper


@app.before_request
def jwt_authentication():
    """
    1.get the Authorization field(token) in HTTP header
    2.Use the jwt module for verification
    3.Judging the verification result, if true, extract the payload information in the token and assign it to
      the Object g to save
    """
    auth = request.headers.get('Authorization')
    g.auth = auth
    # request the authentication server (login.py)
    # if not auth:
    #     return {'code': 401, 'message': 'Please login first.'}, 401
    if auth is not None:
        response = requests.get('http://127.0.0.1:5000/auth', headers={'Authentication': auth})
        data = response.json()
        g.username = data['message']



### HELPER FUNCTIONS ###
# generate url id
def generate_id():
    """
        Generates a new identifier.

        Does so by 'decoding' the global next_id number to a string of
        characters in ALLOWED_ID_CHARACTERS.

        The easiest to see how this works is by using a base of 10.
        Suppose the next_id is 4242. Now, we iterate through each digit (=each
        digit in base 10), and use that digit as an index in our list of
        characters.

        To get the rightmost digit, we can simply take the module with the base
        (4242 % 10 = 2). Then, to discard the rightmost digit, we integer
        divide by the base and repeat the process (4242 // 10 = 424).

        For other bases, this works exactly the same, except that we take a
        different modulo and division.
    """

    # Don't forget to mark next_id as global, as otherwise updating it won't update the global variable
    global next_id

    # Define the base for the operation
    base = len(ALLOWED_ID_CHARACTERS)

    # Iterate through the number to divide it into a string of characters (much like binary decoding)
    identifier = ""
    i = next_id
    while True:
        # Get the rightmost 'digit' (i % base) and use that as an index in the list of characters
        identifier += ALLOWED_ID_CHARACTERS[i % base]
        # Discard the rightmost digit
        i = i // base

        # If we've discarded the last non-zero digit, we're done
        if i == 0: break

    # Reverse the identifier to let it be more intuitive
    identifier = identifier[::-1]

    # Done
    next_id += 1
    return identifier


def valid_url(url):
    """
        Tries to match the given URL for correctness.

        Do so by simply matching it to a regular expression that performs this
        check (see the comment at URL_CORRECTNESS_REGEX).
    """

    # Match with the global regex-expression
    return re.match(URL_CORRECTNESS_REGEX, url) is not None


# We mark this function to be called whenever the user provides the root URL ("/") and one of the specified HTTP methods.
@app.route("/", methods=['POST', 'DELETE'])
@login_required
def root():
    """
        Handles everything that falls under the API root (/).

        Three methods (GET, POST and DELETE) are supported, each of which is
        identified by its HTTP method.

        Because this is a bare-bone implementation, each function simply
        returns its "success" status-code and some identifier to know which one
        has been called.

        You can extend these functions to work with the authentication JWT you
        obtained from your authorization service.
    """
    # if request.method == "PUT":
    #     return {'code': 200, 'message': g.username}, 200

    if request.method == "POST":
        # Try to get the URL
        if "url" not in request.form:
            return "URL not specified", 400
        url = request.form["url"]

        # Validate the URL
        if not valid_url(url):
            return "Invalid URL", 400

        # Generate a new identifier
        identifier = generate_id()

        # Insert it into the map
        id_url_map[identifier] = url

        # insert the url_id in the current user dict (for specialize the url access permission)
        value = g.username
        response = requests.post('http://127.0.0.1:5000/url', data={'url_id': identifier, 'username': value})
        result = response.json()
        if result['message'] == 'success':
            return identifier, 201
        else:
            return {'code': 401, 'message': 'User not found! '}, 401

    elif request.method == "DELETE":
        # Clear the list
        # to_remove = list(id_url_map.keys())
        value = g.username
        # get url list of the current user
        response = requests.post('http://127.0.0.1:5000/current_user_url', data={'username': value})
        result = response.json()
        to_remove = result['message']
        if to_remove:
            for k in to_remove:
                del id_url_map[k]
                return 'Delete successfully! ', 200
        else:
            return "Empty", 404


# The GET method remains unprotected since it is public. Get all url keys
@app.route("/", methods=['GET'])
def get_urls():
    # Switch on the method used
    if request.method == "GET":
        # Collect all the results in a JSON map
        # We can simply return a dict, and flask will automatically serialize this to JSON for us
        return {"keys": [k for k in id_url_map]}, 200


# The GET method remains unprotected since it is public. Get url selected by ID
@app.route("/<string:id>", methods=['GET'])
def get_url_id(id):
    # Switch on the method used
    if request.method == "GET":
        # Check to see if we know this one
        if id in id_url_map:
            # We do! Redirect the user to it
            # The redirect() function will automatically set the correct headers and status code
            return redirect(id_url_map[id])
        else:
            # Resource not found
            abort(404)


# We mark this function to be called for any URL that is nested under the root ("/:id").
# The syntax of the identifier is '<string:id>', which tells flask it's a string (=any non-slash text) that is named 'id'
@app.route("/<string:id>", methods=['PUT', 'DELETE'])
@login_required
def url(id):
    """
        Handles everything that falls under a URL that is an identifier (/:id).

        Three methods (GET, POST and DELETE) are supported, each of which is
        identified by its HTTP method.

        Because this is a bare-bone implementation, each function simply
        returns its "success" status-code and some identifier to know which one
        has been called.

        You can extend these functions to work with the authentication JWT you
        obtained from your authorization service.
    """
    """
        Handles everything that falls under a URL that is an identifier (/:id).

        Methods:
         - GET: Returns the URL behind the given identifier as a 301 result (moved permanently) so the browser automatically redirects.
         - PUT: Updates the given ID to point to the given URL (as a POST field). Returns a 200 on success, 400 on failure or 404 on not-existing ID.
         - DELETE: Deletes the ID/URL mapping based on the ID given, returning a 204 (no content).
    """

    if request.method == "PUT":
        # Check if we know the ID
        if id not in id_url_map:
            abort(404)

        # Try to get the URL
        if "url" not in request.form:
            return "URL not specified", 400
        url = request.form["url"]

        # Validate the URL
        if not valid_url(url):
            return "Invalid URL", 400

        value = g.username
        response = requests.post('http://127.0.0.1:5000/verify_user', data={'url_id': id, 'username': value})
        result = response.json()
        if result['message'] == 'success':
            # Update the ID
            id_url_map[id] = url
            return "success", 200
        else:
            return {'code': 401, 'message': 'Permission denied! '}, 401

    elif request.method == "DELETE":
        # Check if it exists
        if id in id_url_map:
            value = g.username
            response = requests.post('http://127.0.0.1:5000/verify_user', data={'url_id': id, 'username': value})
            result = response.json()
            if result['message'] == 'success':
                # Remove it, then success
                del id_url_map[id]
                return "success", 204
            else:
                return {'code': 401, 'message': 'Permission denied! '}, 401
        else:
            # Resource not found
            abort(404)
