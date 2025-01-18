from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def home():
    files_in_directory = os.listdir()
    response = "Files in directory: <br>"
    for file in files_in_directory:
        response += f'<a href="/get-file/{file}">{file}</a><br>'
    return response

@app.route('/get-file/<path:filename>', methods=['GET'])
def get_file(filename):
    return send_from_directory('.', filename, as_attachment=False)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)