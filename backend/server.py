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
    """
    If login successfully:
    {
        "message": "Login successful", 
        "username": username
    }

    else:
    {
        "message": "Invalid email or password"
    }
    """
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
            response = {"message": "Invalid email or password"}
        else:
            # Check if the password is correct
            stored_password = user[1]  # Assuming the password is stored in the second column
            if password == stored_password:
                # If the password is correct, include the username in the response
                username = user[2]  # Assuming the username is stored in the third column
                response = {"message": "Login successful", "username": username}
            else:
                response = {"message": "Invalid email or password"}

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
    """
    {
        "data": [
        {
            "AthleteId": 91,
            "Country": "Poland",
            "Discipline": "Athletics",
            "Name": "ADAMEK Klaudia",
            "RateeId": 90
        }]
    }

    """
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
            filter_conditions = " AND ".join([f"{key}= '{value}'" for key, value in filters.items()])
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
    """
    {
        "data": {
            "AthleteId": 4,
            "Comments": [
                {
                    "CommentId": 0,
                    "Content": "test",
                    "PostBy": "123@123",
                    "Target": 3,
                    "Time": "Sat, 25 Nov 2023 18:16:52 GMT"
                },
                {
                    "CommentId": 0,
                    "Content": "test",
                    "PostBy": "123@123",
                    "Target": 3,
                    "Time": "Sat, 25 Nov 2023 18:19:54 GMT"
                },
                {
                    "CommentId": 0,
                    "Content": "bad player",
                    "PostBy": "123@123",
                    "Target": 3,
                    "Time": "Sat, 25 Nov 2023 18:59:24 GMT"
                }
            ],
            "Country": "Spain",
            "Discipline": "Basketball",
            "Name": "ABALDE Alberto",
            "RateeId": 3,
            "Rating": 0,
            "Type": "Athlete"
        }
    }
    """
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
def get_athlete_by_discipline():
    """
    {
        "data": [
        {
            "AthleteId": 91,
            "Country": "Poland",
            "Discipline": "Athletics",
            "Name": "ADAMEK Klaudia",
            "RateeId": 90
        }]
    }

    """
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
def get_athlete_by_country():
    """
    {
        "data": [
        {
            "AthleteId": 91,
            "Country": "Poland",
            "Discipline": "Athletics",
            "Name": "ADAMEK Klaudia",
            "RateeId": 90
        }]
    }
    

    """
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
    
@app.route('/api/medal', methods=['GET'])
def get_medal():
    """
    {
        "data": [
        {
            "Bronze": 33,
            "Country": "United States of America",
            "Gold": 39,
            "Ranks": 1,
            "Silver": 41
        },
        {
            "Bronze": 18,
            "Country": "People's Republic of China",
            "Gold": 38,
            "Ranks": 2,
            "Silver": 32
        }]
    }
    

    """
    try:
        conn = mysql.connector.connect(**db_config)

        cursor = conn.cursor()
        query = f"SELECT * FROM Country c ORDER BY c.Ranks"
        cursor.execute(query)
        return {'data': [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]}

    except Exception as e:
        return {"error": str(e)}


# just call it
@app.route('/api/fun-facts', methods=['GET'])
def fun_facts():
    """
    {
    "data": [
        [
            {
                "Discipline": "Water Polo",
                "PlayerToCoachRatio": "12.1818"
            },
            {
                "Discipline": "Rugby Sevens",
                "PlayerToCoachRatio": "11.8800"
            },
            {
                "Discipline": "Handball",
                "PlayerToCoachRatio": "11.5862"
            }
        ],
        [
            {
                "Athlete_to_Medal_Ratio": "45510.0256",
                "Country": "United States of America",
                "Number_of_Athletes": 615,
                "Total_medals": "69495"
            },
            {
                "Athlete_to_Medal_Ratio": "20050.0263",
                "Country": "People's Republic of China",
                "Number_of_Athletes": 401,
                "Total_medals": "35288"
            }
        ]
    }
    """
    try:
        conn = mysql.connector.connect(**db_config)
        query1 = ("SELECT Discipline, TotalPlayerCount/CountNum AS PlayerToCoachRatio FROM Discipline NATURAL JOIN ("
                  "SELECT COUNT(CoachID) AS CountNum, Discipline FROM Coach GROUP BY Discipline) AS CoachCount ORDER "
                  "BY PlayerToCoachRatio DESC LIMIT 15;")
        cursor = conn.cursor()
        cursor.execute(query1)
        res1 = [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]

        query2 = ("SELECT A.Country, COUNT(A.AthleteId) AS Number_of_Athletes, SUM(C.Gold) + SUM(C.Silver) + SUM("
                  "C.Bronze) AS Total_medals, COUNT(A.AthleteId) / SUM(C.Gold) + SUM(C.Silver) + SUM(C.Bronze) AS "
                  "Athlete_to_Medal_Ratio FROM Athlete A JOIN Country C ON A.Country = C.Country GROUP BY A.Country "
                  "ORDER BY Athlete_to_Medal_Ratio DESC LIMIT 15;")
        cursor = conn.cursor()
        cursor.execute(query2)
        res2 = [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]
        return {'data': [res1, res2]}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
