import pickle
from datetime import datetime

import mysql.connector
from flask import Flask, request, jsonify

from helper import retrieve_data

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
    "database": "test",
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
    rating = 0

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
        existing_user = cursor.rowcount

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
        user = cursor.rowcount

        if user == 0:
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


# /filter?table=athlete&order_by=C&order=desc&filters={Country:China,Name:A}
@app.route('/api/filter', methods=['GET'])
def query_table():
    try:
        conn = mysql.connector.connect(**db_config)
        table_name = request.args.get('table')
        order_by = request.args.get('order_by')
        order = request.args.get('order')
        filters = request.args.get('filters')

        query = f"SELECT * FROM {table_name}"
        if not table_name: return {"error": "table not specified"}
        if filters:
            filters = dict(item.split(":") for item in filters[1:-1].split(","))
            filter_conditions = " AND ".join([f"'{key}'= '{value}'" for key, value in filters.items()])
            query += f" WHERE {filter_conditions}"

        if order_by and order:
            query += f" ORDER BY {order_by} {order}"
        cursor = conn.cursor()
        cursor.execute(query)

        return {'data': [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]}
    except Exception as e:
        return {"error": str(e)}


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        conn = mysql.connector.connect(**db_config)

        query = ""
        cursor = conn.cursor()
        cursor.execute(query)

        return {'data': [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]}
    except Exception as e:
        return {"error": str(e)}


# /ratee?rateeid=3
@app.route('/api/ratee', methods=['GET'])
def get_ratee_info():
    try:
        conn = mysql.connector.connect(**db_config)

        rateeid = request.args.get('rateeid')
        if not rateeid: return {"error": "rateeid not specified"}

        cursor = conn.cursor()
        query = f"SELECT * FROM Ratee WHERE Rateeid = '{rateeid}' LIMIT 1"
        cursor.execute(query)

        ratee_info = cursor.fetchall()[0]
        if not ratee_info: return {"error": "ratee not found"}
        type = ratee_info[1]
        rating = ratee_info[2] / ratee_info[3] if ratee_info[3] else 0
        rating_info = {"Type": type, "Rating": rating}

        query = f"SELECT * FROM {type} WHERE Rateeid = '{rateeid}' LIMIT 1"
        cursor.execute(query)
        other_info = dict(zip(cursor.column_names, cursor.fetchall()[0]))

        query = f"SELECT * FROM Comment WHERE Target = '{rateeid}'"
        cursor.execute(query)
        comments = {"Comments": [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]}

        return {'data': {**rating_info, **other_info, **comments}}

    except Exception as e:
        return {"error": str(e)}
    # Get ratee information


# {"content":"test","email":"123@123","target":3}
@app.route('/api/comment', methods=['POST'])
def post_comment():
    try:

        conn = mysql.connector.connect(**db_config)

        data = request.get_json()
        content = data["content"]
        email = data["email"]
        target = data["target"]

        conn.start_transaction()
        cursor = conn.cursor()
        query = (f"INSERT INTO Comment (Content, Time, PostBy, Target) VALUES ('{content}', "
                 f"'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}', '{email}', {target})")
        cursor.execute(query)
        res = cursor.rowcount
        conn.commit()

        return jsonify({"message": "Comment posted"}) if res else jsonify({"message": "Invalid comment"})


    except Exception as e:
        response = {"error": str(e)}
        if conn: conn.rollback()
        return jsonify(response)


# {"rate_by":"test","rating_value":"3","target":3}
@app.route('/api/rates', methods=['POST'])
def post_rate():
    try:
        conn = mysql.connector.connect(**db_config)

        data = request.get_json()
        rate_by = data["rate_by"]
        target = data["target"]
        rating_value = data["rating_value"]

        conn.start_transaction()
        cursor = conn.cursor()
        query = (f"INSERT INTO Rates (RateBy, Target, RatingValue, Time) VALUES ('{rate_by}', "
                 f"{target}, {rating_value}, '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')")
        cursor.execute(query)
        res = cursor.rowcount
        conn.commit()

        return jsonify({"message": "Rating posted"}) if res else jsonify({"message": "Invalid rating"})

    except Exception as e:
        response = {"error": str(e)}
        if conn: conn.rollback()
        return jsonify(response)


# /discipline?discipline=Tennis
@app.route('/api/discipline', methods=['GET'])
def get_by_discipline():
    try:
        conn = mysql.connector.connect(**db_config)

        discipline = request.args.get('discipline')
        if not discipline: return {"error": "discipline not specified"}

        cursor = conn.cursor()
        query = f"SELECT * FROM Athlete WHERE Discipline = '{discipline}'"
        cursor.execute(query)
        return {'data': [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]}

    except Exception as e:
        return {"error": str(e)}


# /country?country=Poland
@app.route('/api/country', methods=['GET'])
def get_by_country():
    try:
        conn = mysql.connector.connect(**db_config)

        country = request.args.get('country')
        if not country: return {"error": "country not specified"}

        cursor = conn.cursor()
        query = f"SELECT * FROM Athlete WHERE Country = '{country}'"
        cursor.execute(query)
        return {'data': [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
