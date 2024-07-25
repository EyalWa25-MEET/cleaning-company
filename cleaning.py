from flask import Flask, render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pyrebase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


firebase_config = {
'apiKey': "AIzaSyDM45mNofwWDKdY9HgvkUxBNOjfU3tjGbw",
'authDomain': "cleaning-2c1e4.firebaseapp.com",
'databaseURL': "https://cleaning-2c1e4-default-rtdb.europe-west1.firebasedatabase.app",
'projectId': "cleaning-2c1e4",
'storageBucket': "cleaning-2c1e4.appspot.com",
'messagingSenderId': "311981548917",
'appId': "1:311981548917:web:2177ada349c6ab86f41f3c",
'measurementId': "G-F7PDRL6BRT"
};
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

class User(UserMixin):
    def __init__(self, uid, email):
        self.id = uid
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    user_data = db.child("users").child(user_id).get().val()
    if user_data:
        return User(user_id, user_data['email'])
    return None


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ClientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    forms = ClientForm()
    if forms.validate_on_submit():
        client_data = {
            'name': form.name.data,
            'address': form.address.data,
            'user_id': current_user.id
        }
        db.child("clients").push(client_data)
        flash('Request submitted successfully!', 'success')
        return redirect(url_for('index'))
    return render_template( 'form.html', form=form )

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = auth.create_user_with_email_and_password(form.email.data, form.password.data)
            db.child("users").child(user['localId']).set({'email': form.email.data})
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except:
            flash('An error occurred. Please try again.', 'danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = auth.sign_in_with_email_and_password(form.email.data, form.password.data)
            user_info = auth.get_account_info(user['idToken'])
            user_id = user_info['users'][0]['localId']
            login_user(User(user_id, form.email.data))
            return redirect(url_for('index'))
        except:
            flash('Login failed. Please check your email and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
