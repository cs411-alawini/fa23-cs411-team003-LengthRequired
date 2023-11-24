import requests
import time
import os
import io
import warnings
import threading
import subprocess
import pickle
from flask import Flask, request, jsonify, make_response, Response
from flask_cors import CORS, cross_origin
import mysql.connector


pickle_file_path = 'config.pickle'

# Load the dictionary from the pickle file
with open(pickle_file_path, 'rb') as file:
    loaded_dict = pickle.load(file)

USER = loaded_dict["user"]
PASSWORD = loaded_dict["password"]
HOST = loaded_dict["host"]

app = Flask(__name__)


db_config = {
    "user": USER,
    "password": PASSWORD,
    "host": HOST,
    "database": "db",
}

# Establish a connection to the database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()



@app.route('/', methods=['GET', 'POST'])
def home():
    return 'Hello, World!'


# Define a JSON API endpoint
@app.route('/api/rating', methods=['GET'])
def get_rating():
    ratee_data = request.get_json()
    data = {'message': 'This is data from the backend!'}
    return jsonify(data)


@app.route('/api/registration', methods=['POST'])
def register():
    user_data = request.get_json()
    email = user_data["email"]
    password = user_data["password"]
    username = user_data["username"]

    #Validate whether email is already existed

    #Insert to mysql


@app.route('/api/login', methods=['GET'])
def login():
    user_data = request.get_json()

    #validate whether the username and password pair is valid
    #Select password from User table using email


@app.route('/api/table', methods=['GET'])
def query_table():
    filters = request.get_json()

    #Get table infor based on filters




@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    data = request.get_json()

    # Get country information with count of metals and orders


@app.route('/api/ratee', methods=['GET'])
def get_leaderboard():
    data = request.get_json()
    name = data["name"]
    type = data["type"]

    # Get ratee information


@app.route('/api/comment', methods=['POST'])
def post_comment():
    data = request.get_json()
    content = data["content"]
    email = data["email"]


if __name__ == "__main__":
    app.run()