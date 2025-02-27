from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def is_strong_password(password):
    # Check if the password is at least 8 characters long
    if len(password) < 8:
        return False
    # Check if the password contains both uppercase and lowercase letters
    if not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password):
        return False
    # Check if the password contains at least one numerical digit
    if not re.search(r'\d', password):
        return False
    # Check if the password contains at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if not is_strong_password(password):
        return jsonify({'message': 'Password is not strong enough'}), 400

    # Here you would normally save the user to the database
    # For this example, we'll just return a success message

    return jsonify({'message': 'User signed up successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
