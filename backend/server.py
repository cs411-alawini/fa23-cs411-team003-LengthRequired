import requests
import time
import os
import io
import warnings
import threading
import subprocess

from flask import Flask, request, jsonify, make_response, Response
from flask_cors import CORS, cross_origin


app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def home():
    return 'Hello, World!'


# Define a JSON API endpoint
@app.route('/api/get-rating', methods=['GET'])
def get_rating():
    data = {'message': 'This is data from the backend!'}
    return jsonify(data)

@app.route('/api/sign_up', methods=['POST'])
def sign_up():
    user_data = request.get_json()
    email = user_data["email"]
    password = user_data["password"]
    username = user_data["username"]

    #Validate whether email is already existed

    #Insert to mysql


@app.route('/api/login', methods=['POST'])
def sign_up():
    user_data = request.get_json()

    #validate whether the username and password pair is valid
    #Select password from User table using email






if __name__ == "__main__":
    app.run()