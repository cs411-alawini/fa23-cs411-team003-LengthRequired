# helper functions for backend


def retrieve_data(cursor, command):
    cursor.execute(command)
    data = cursor.fetchall()
    return data


# def insert_data(cursor, insert_query, values):
#     cursor.execute(insert_query, values)
