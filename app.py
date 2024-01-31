from flask import Flask, render_template, session, redirect, request, url_for, flash
import csv
import flask_login
from flask_login import UserMixin, LoginManager, login_user
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from wtforms import StringField , PasswordField , SubmitField
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://doadmin:AVNS_Ed7FVk0dyVGlhXuZmb4@db-postgresql-lon1-41546-do-user-14798294-0.c.db.ondigitalocean.com:25060/defaultdb?sslmode=require'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = '1234'
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'support@voteforproduct.com'  # Replace with your Gmail address
app.config['MAIL_PASSWORD'] = 'RobbieIsCool'         # Replace with your Gmail password or app password
mail = Mail(app)

current_date = '31 JAN'
guild_events = []
with open('events.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        guild_events.append([row[0], row[1], row[2], row[3]])

guild_events_to_display = []
for event in guild_events:
    if event[1] == current_date:
        guild_events_to_display.append(event)


@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)



# Registration Form
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=5, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        email_domain = form.email.data.split('@')[-1]
        print(email_domain)
        if email_domain != 'exeter.ac.uk':
            flash("Email must end in exeter.ac.uk.")
            return redirect (url_for('register'))
        if User.query.filter_by(email=email).first():  # the query has returned a user
            flash("Email already in use, please log in or use a different email.")
            return redirect (url_for('register'))
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration Successful !')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/verify')
def verify():
    return render_template('verify.html')

@app.route('/verify54321', methods=['GET', 'POST'])
def complete_verification():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        is_valid = bcrypt.check_password_hash(user.password, password)
        if user and is_valid:
            user.is_confirmed = True
            db.session.commit()
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Verification failed , check your username and password', 'danger')
    return render_template('verify54321.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        is_valid = bcrypt.check_password_hash(user.password, password)
        if user and is_valid and user.is_confirmed:
            login_user(user)
            return redirect(url_for('home'))

        if user and is_valid and user.is_confirmed is False:
            msg = Message(subject='WhatAmIGonnaDoTonight Verification',
                          sender='support@voteforproduct.com',  # Replace with your Gmail address
                          recipients=[email])  # Replace with your Gmail address
            msg.body = (
                        'Thanks for signing up!\n\nI\'m using my support@voteforproduct.com email address to verify users ' +
                        'because I can\'t afford to buy an email address for this domain.\n\n' +
                        'Click this link to verify your email:\n\nhttps://whatamigonnadotonight.com/verify54321\n\n' +
                        'Also please don\'t share this link with anyone else. I really didn\'t spend a lot of time ' +
                        'on email verification so if you share this anyone can sign up.')
            mail.send(msg)
            return redirect(url_for('verify'))
        else:
            flash('login failed , check your username and password', 'danger')
    return render_template('login.html')

@app.route('/')
def home():
    user = flask_login.current_user
    if user.is_anonymous or user.is_confirmed is False:
        return redirect(url_for('login'))
    return render_template('index.html', events=guild_events_to_display)


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)