import pickle
from datetime import datetime

import mysql.connector
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin

pickle_file_path = 'config.pickle'

# Load the dictionary from the pickle file
with open(pickle_file_path, 'rb') as file:
    loaded_dict = pickle.load(file)

USER = loaded_dict["user"]
PASSWORD = loaded_dict["password"]
HOST = loaded_dict["host"]

app = Flask(__name__)
CORS(app)

db_config = {
    "user": USER,
    "password": PASSWORD,
    "host": HOST,
    "database": "db",
}


@app.route('/', methods=['GET', 'POST'])
def home():
    return 'Hello, World!'


@app.route('/api/registration', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        # Handle OPTIONS request
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.status_code = 200
        return response

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        if request.method == 'POST':
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
                if cursor.rowcount > 0:
                    response = {"message": "User registered successfully."}
                    status_code = 200
                else:
                    response = {"message": "User registration failed."}
                    status_code = 500  # or any appropriate error status code

            return jsonify(response), status_code

    except Exception as e:
        response = {"error": str(e)}
        return jsonify(response), 500  # Internal Server Error

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
            return jsonify(response), 401
        else:
            # Check if the password is correct
            stored_password = user[1]  # Assuming the password is stored in the second column
            if password == stored_password:
                # If the password is correct, include the username in the response
                username = user[2]  # Assuming the username is stored in the third column
                response = {"message": "Login successful", "username": username}
            else:
                response = {"message": "Invalid email or password"}
                return jsonify(response), 401
            return jsonify(response)


    except Exception as e:
        response = {"error": str(e)}
        return jsonify(response), 500

    finally:
        cursor.close()
        conn.close()


# /filter?table=athlete&order_by=C&order=desc&country=China&name=A}
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
        country = request.args.get('country')
        name = request.args.get('name')
        filters = {}
        if country:
            filters['Country'] = country
        if name:
            filters["Name"] = name

        if not table_name:
            return {"error": "table not specified"}, 400

        query = f"SELECT * FROM {table_name}"

        if filters:
            # filters = dict(item.split(":") for item in filters[1:-1].split(","))
            filter_conditions = " AND ".join([f"{key}= \"{value}\"" for key, value in filters.items()])
            query += f" WHERE {filter_conditions}"

        if order_by and order:
            query += f" ORDER BY {order_by} {order}"

        cursor = conn.cursor()
        cursor.execute(query)

        return jsonify({'data': [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        if not rateeid: return {"error": "rateeid not specified"},400

        cursor = conn.cursor()
        query = f"SELECT * FROM Ratee WHERE Rateeid = '{rateeid}' LIMIT 1"
        cursor.execute(query)

        ratee_info = cursor.fetchall()[0]
        if not ratee_info: return {"error": "ratee not found"},404
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
        return {"error": str(e)},500
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
        comment_id = cursor.lastrowid
        conn.commit()

        return jsonify({"message": "Comment posted", "CommentId": comment_id}),200 if res else jsonify(
            {"message": "Invalid comment"}),400

    except Exception as e:
        response = {"error": str(e)}
        if conn: conn.rollback()
        return jsonify(response),500


@app.route('/api/comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    try:
        conn = mysql.connector.connect(**db_config)

        conn.start_transaction()
        cursor = conn.cursor()
        query = "DELETE FROM Comment WHERE CommentID = %s"
        cursor.execute(query, (comment_id,))
        res = cursor.rowcount
        conn.commit()

        if res:
            return jsonify({"message": "Comment deleted"}), 200
        else:
            return jsonify({"message": "Invalid comment ID"}), 404

    except Exception as e:
        response = {"error": str(e)}
        if conn:
            conn.rollback()
        return jsonify(response), 500


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

        check_query = f"SELECT * FROM Rates WHERE RateBy = '{rate_by}' AND Target = {target}"
        cursor.execute(check_query)
        res = cursor.fetchall()

        if res:
            query = (f"UPDATE Rates SET RatingValue = {rating_value}, Time = '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' "
                     f"WHERE RateBy = '{rate_by}' AND Target = {target}")
            message = "Rating updated"
        else:
            query = (f"INSERT INTO Rates (RateBy, Target, RatingValue, Time) VALUES ('{rate_by}', "
                     f"{target}, {rating_value}, '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')")
            message = "Rating posted"

        cursor.execute(query)
        res = cursor.rowcount
        conn.commit()

        return jsonify({"message": message}),200 if res else jsonify({"message": "Invalid rating"}),400

    except Exception as e:
        response = {"error": str(e)}
        if conn: conn.rollback()
        return jsonify(response),500


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
        if not discipline: return {"error": "discipline not specified"},400

        cursor = conn.cursor()
        query = f"SELECT * FROM Athlete WHERE Discipline = '{discipline}'"
        cursor.execute(query)

        return {'data': [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]}

    except Exception as e:
        return {"error": str(e)},500


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
        if not country: return {"error": "country not specified"},400

        cursor = conn.cursor()
        query = f"SELECT * FROM Athlete WHERE Country = '{country}'"
        cursor.execute(query)
        return {'data': [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]}

    except Exception as e:
        return {"error": str(e)},500


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
        return {"error": str(e)},500


# Retrieve the result from the stored procedure
"""
DELIMITER //
CREATE PROCEDURE PlayerRank()
BEGIN
	DECLARE varRateeId INT;
	DECLARE varName VARCHAR(50);
	DECLARE varScore DOUBLE;
	DECLARE varRank VARCHAR(2);
	DECLARE done BOOLEAN DEFAULT FALSE;
	DECLARE cur CURSOR FOR (SELECT RateeId, Name, (IFNULL(Rating/Average, 0)*0.8+CommentCount*0.2) AS Score FROM RatingComment NATURAL JOIN DisciplineAverage);
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
	DROP TEMPORARY TABLE IF EXISTS RatingComment; 
    DROP TEMPORARY TABLE IF EXISTS DisciplineAverage; 
	CREATE TEMPORARY TABLE RatingComment AS
	(SELECT RateeId, Name, CommentCount, (SumofRating/NULLIF(NumofRating, 0)) AS Rating, Discipline FROM Athlete NATURAL JOIN Ratee NATURAL JOIN (SELECT Target AS RateeId, COUNT(*) AS CommentCount FROM Comment GROUP BY Target) AS Temp);
	CREATE TEMPORARY TABLE DisciplineAverage AS
	(SELECT Discipline, AVG(SumofRating/NULLIF(NumofRating, 0)) AS Average FROM Ratee NATURAL JOIN Athlete GROUP BY Discipline);
	DROP TABLE IF EXISTS FinalTable;
	CREATE TABLE FinalTable (RateeId INT PRIMARY KEY, Name VARCHAR(50), PlayerRank VARCHAR(2), Score DOUBLE);
	OPEN cur;
		Cloop: LOOP
		FETCH cur INTO varRateeId, varName, varScore;
        IF done THEN
            LEAVE cloop;
        END IF;

        IF varScore >= 5.1 THEN
            SET varRank = 'A';
        ELSEIF varScore >= 2.8 THEN
            SET varRank = 'B';
        ELSE
            SET varRank = 'C';
        END IF;

        INSERT INTO FinalTable VALUE (varRateeId, varName, varRank, varScore);
        END LOOP cloop;
    CLOSE cur;

	SELECT * FROM FinalTable ORDER BY PlayerRank;
END//
DELIMITER ;

"""


@app.route('/api/player-rank', methods=['GET'])
def player_rank():
    """
    "data": [
        {
            "Name": "ABALDE Alberto",
            "PlayerRank": "C",
            "RateeId": 3,
            "Score": 0.8
        },
        {
            "Name": "ABALO Luc",
            "PlayerRank": "C",
            "RateeId": 5,
            "Score": 1.0
        }]
    
    
    
    
    """
    try:
        conn = mysql.connector.connect(**db_config)
        dict_cursor = conn.cursor(dictionary=True)
        dict_cursor.callproc("PlayerRank")
        results = next(dict_cursor.stored_results()).fetchall()
        return {'data': results}

    except Exception as e:
        return {"error": str(e)},500


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
        return {"error": str(e)},500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
