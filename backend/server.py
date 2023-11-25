import requests
import time
import os
import io
import warnings
import threading
import subprocess
import pickle
from helper import retrieve_data
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



@app.route('/', methods=['GET', 'POST'])
def home():
    return 'Hello, World!'


# Define a JSON API endpoint
@app.route('/api/rating', methods=['GET'])
def get_rating():
    # Establish a connection to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    ratee_data = request.get_json()
    name = ratee_data['name']
    type = ratee_data['type']

    # Get corresponding table
    command = ""
    data = retrieve_data(command)

    # Use name and type to get desired info from data
    rating = None

    return jsonify(rating)


@app.route('/api/registration', methods=['POST'])
def register():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        user_data = request.get_json()
        email = user_data["email"]
        password = user_data["password"]
        username = user_data["username"]

        # Validate whether email is already existed
        cursor.execute("SELECT * FROM User WHERE Email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            response = {"message": "User with this email already exists."}
        else:
            # Insert into MySQL
            insert_query = "INSERT INTO User (Email, Password, Username) VALUES (%s, %s, %s)"
            user_values = (email, password, username)
            cursor.execute(insert_query, user_values)
            conn.commit()
            response = {"message": "User registered successfully."}

        return jsonify(response)

    except Exception as e:
        response = {"error": str(e)}
        return jsonify(response)

    finally:
        cursor.close()
        conn.close()



@app.route('/api/login', methods=['POST'])
def login():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        user_data = request.get_json()
        email = user_data["email"]
        password = user_data["password"]

        # Validate whether the email exists
        cursor.execute("SELECT * FROM User WHERE Email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            response = {"message": "Invalid email or password."}
        else:
            # Check if the password is correct
            stored_password = user[1]
            if password == stored_password:
                response = {"message": "Login successful!"}
            else:
                response = {"message": "Invalid email or password."}

        return jsonify(response)

    except Exception as e:
        response = {"error": str(e)}
        return jsonify(response)

    finally:
        cursor.close()
        conn.close()


@app.route('/api/table', methods=['GET'])
def query_table():
    filters = request.get_json()

    #Get table infor based on filters




@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    data = request.get_json()

    # Get country information with count of metals and orders


@app.route('/api/ratee', methods=['GET'])
def get_ratee_info():
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