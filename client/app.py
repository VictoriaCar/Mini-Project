# ChatGPT used for interface, including files: flaskblog.py | login/register/home/dashboard.hmt | style.css
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm 
import requests # For sentiment analysis
from flask_sqlalchemy import SQLAlchemy
import socket
import json

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = '129jasapowqe;[]/oiwq498498'  # Replace with your secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Adjust the database URI as needed

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

host = '3.130.58.56'  # Loopback address for local testing
port = 7807

sessions = []
chat_messages = []


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

def create_client_socket(packet):
    global host
    global port
    # socket request to get data
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    json_data = json.dumps(packet)
    
    # Connect to the server
    client_socket.connect((host, port))
    client_socket.send(json_data.encode())

    data = client_socket.recv(1024) # this will preempt the app; 
    data.decode()

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

    # Sentiment Analysis
def perform_sentiment_analysis(text, language):
    api_key = '0e1d08c813b3f2b41a1eb789b98ab2d5'
    url = 'https://api.meaningcloud.com/sentiment-2.1'

    payload = {
        'key': api_key,
        'txt': text,
        'lang': 'en',  
    }

    response = requests.post(url, data=payload)
    return response.json()

# # Load user function for Flask-Login
# @login_manager.user_loader
# def load_user(user_id):
#     # create a thread task for client socket
#     # we want to GET asynch
#     packet = {
#         "cmd" : "AUTH",
#         "user_id" : user_id,
#     }
    
#     user = json.loads(create_client_socket(packet).decode())
#     user_obj = User(user.user_id)

#     return None if not user_obj else user_obj

# # Create the database tables
# with app.app_context():
#     db.create_all()

# Rest of your app routes and logic
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Create a new user based on the registration form data
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(email=form.email.data, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Add the new user to the database
            # socket request to AWS server
        # packet = {
        #     "cmd" : "REGISTER",
        #     "email" : form.email.data,
        #     "key" : hashed_password,
        # }
        # user = json.loads(create_client_socket(packet).decode())
        # new_user_obj = User(user.uid)

        print(new_user)
        # Log the new user in after successful registration
        login_user(new_user)
        # sessions.append(user.uid)

        flash('Your account has been created! You are now logged in.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    global sessions
    # socket request to get the database
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        # socket request to find user
        # packet = {
        #     "cmd" : "LOGIN",
        #     "email" : form.email.data,
        # }

        # user = json.loads(create_client_socket(packet).decode()) # from firebase
        # user_obj = User(user['AUTH'].uid)

        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # sessions.append(user['AUTH'].uid)

            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')

    return render_template('login.html', form=form)

# Route for the dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        text = request.form['text']
        language = request.form['language']

        if text and language:
            # Analyze the sentiment of the user's message
            sentiment_result = perform_sentiment_analysis(text, language)
            chat_messages.append((text, sentiment_result))

    return render_template('dashboard.html', chat_messages=chat_messages)

    # Aanalyze_sentiment route 
@app.route('/analyze_sentiment', methods=['POST'])
@login_required
def analyze_sentiment():
    text = request.form['text']
    language = request.form['language']

    if text and language:
        # Analyze the sentiment of the user's message
        sentiment_result = perform_sentiment_analysis(text, language)
        return jsonify(sentiment_result)

    return jsonify({'error': 'Invalid request'}), 400

@app.route('/process_msg', methods=['GET', 'POST'])
def processMessage():
    if request.method == 'POST':
        try:
            data = request.get_json()  # This will parse the JSON data sent from the client
            # You can now work with the 'data' variable, which will contain your JavaScript array
            # For example, you can process the array and return a response

            packet = {
                "cmd" : "SET",
                "email" : current_user.email,
                "username" : current_user.email,
                "message" : data,
            }
            create_client_socket(packet)
            
            print(data)
        except Exception as e:
            pass
        
    return render_template('dashboard.html')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

