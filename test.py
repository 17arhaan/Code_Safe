"""
Vulnerable Python Application - Test File for Code Safe
This file contains intentional security vulnerabilities for demonstration purposes.
"""

import os
import subprocess
import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Vulnerability 1: Remote Code Execution (RCE) via eval
@app.route('/calculate')
def calculate():
    user_input = request.args.get('expression', '')
    # VULNERABLE: Direct eval of user input
    result = eval(user_input)
    return f"Result: {result}"

# Vulnerability 2: Command Injection via subprocess
@app.route('/ping')
def ping():
    host = request.args.get('host', 'localhost')
    # VULNERABLE: Unsanitized input to shell command
    output = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return output

# Vulnerability 3: SQL Injection
@app.route('/user')
def get_user():
    user_id = request.args.get('id', '')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # VULNERABLE: Direct string concatenation in SQL query
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    user = cursor.fetchone()
    return str(user)

# Vulnerability 4: Cross-Site Scripting (XSS)
@app.route('/greet')
def greet():
    name = request.args.get('name', 'Guest')
    # VULNERABLE: Unsanitized input rendered in template
    template = f"<html><body>Hello {name}!</body></html>"
    return render_template_string(template)

# Vulnerability 5: Local File Inclusion (LFI)
@app.route('/read')
def read_file():
    filename = request.args.get('file', 'default.txt')
    # VULNERABLE: User-controlled file path
    with open(filename, 'r') as f:
        content = f.read()
    return content

# Vulnerability 6: Server-Side Request Forgery (SSRF)
@app.route('/fetch')
def fetch_url():
    import requests
    url = request.args.get('url', '')
    # VULNERABLE: User-controlled URL without validation
    response = requests.get(url)
    return response.text

# Vulnerability 7: Arbitrary File Write (AFO)
@app.route('/save')
def save_file():
    filename = request.args.get('filename', 'output.txt')
    content = request.args.get('content', '')
    # VULNERABLE: User-controlled file path
    with open(filename, 'w') as f:
        f.write(content)
    return "File saved!"

# Vulnerability 8: Insecure Direct Object Reference (IDOR)
@app.route('/profile/<user_id>')
def view_profile(user_id):
    # VULNERABLE: No access control check
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    profile = cursor.fetchone()
    return str(profile)

# Additional RCE vulnerability
def execute_command(cmd):
    # VULNERABLE: Using os.system with user input
    os.system(cmd)

# Deserialization vulnerability
import pickle

@app.route('/load')
def load_data():
    data = request.args.get('data', '')
    # VULNERABLE: Unsafe deserialization
    obj = pickle.loads(data.encode())
    return str(obj)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

