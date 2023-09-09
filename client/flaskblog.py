from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

#Welcome page/Login page
@app.route("/")
def welcome():
    return render_template('welcome.html')

#Chat page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if users.get(username) == password:
            return f'Welcome, {username}!'
        else:
            return 'Invalid credentials. Please try again.'

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
