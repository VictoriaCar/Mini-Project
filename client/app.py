from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm 
import socket
import json

app = Flask(__name__, template_folder='templates')

login_manager = LoginManager(app)
login_manager.login_view = 'login'

host = '3.130.58.56'  # Loopback address for local testing
port = 7807

# Define the User model class
class User(UserMixin):
    id = ""
    email = ""
    password = ""

    def __init__(self, id):
        self.id = id

def create_client_socket(packet):
    global host
    global port
    # socket request to get data
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect((host, port))
    client_socket.send(packet.encode())

    data = client_socket.recv(1024) # this will preempt the app; 
    data.decode()

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(email):
    # create a thread task for client socket
    # we want to GET asynch
    cmd = "GET test@test.com"
    user = create_client_socket(cmd)

    return None if not user else user

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
            # socket request to AWS server

        # Log the new user in after successful registration
        login_user(new_user)

        flash('Your account has been created! You are now logged in.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():

    # socket request to get the database
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        # socket request to find user
        user = {} # from firebase
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

