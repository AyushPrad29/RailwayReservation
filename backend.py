from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpassword",
        database="train_reservation"
    )

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO user (user_id, name, phone, email, password) VALUES (%s, %s, %s, %s, %s)",
                       (data['user_id'], data['name'], data['phone'], data['email'], data['password']))
        conn.commit()
        return jsonify({"message": "User registered successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        cursor.close()
        conn.close()

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE user_id = %s AND password = %s", (data['user_id'], data['password']))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return jsonify({"message": "Login successful!"})
    else:
        return jsonify({"error": "Invalid credentials!"})

# Search Trains
@app.route('/search_trains', methods=['GET'])
def search_trains():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM train WHERE origin = %s AND destination = %s", (origin, destination))
    trains = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(trains)

# Book Ticket
@app.route('/book_ticket', methods=['POST'])
def book_ticket():
    data = request.json
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT seats, fare FROM train WHERE train_number = %s", (data['train_number'],))
        train = cursor.fetchone()
        if train and train[0] >= data['seats']:
            total_fare = train[1] * data['seats']
            cursor.execute("INSERT INTO booking (user_id, train_number, seats, fare) VALUES (%s, %s, %s, %s)",
                           (data['user_id'], data['train_number'], data['seats'], total_fare))
            cursor.execute("UPDATE train SET seats = seats - %s WHERE train_number = %s", (data['seats'], data['train_number']))
            conn.commit()
            return jsonify({"message": "Booking successful!"})
        else:
            return jsonify({"error": "Not enough seats available!"})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        cursor.close()
        conn.close()

# Run Flask Server
if __name__ == '__main__':
    app.run(debug=True)
