from flask import Blueprint, render_template, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
from .database import mysql

auth = Blueprint('auth', __name__)

# Registration Form
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (field.data,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError('Email already taken')

# Login Form
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# Register Route
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                       (name, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)

# Login Route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, password FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            user_id, stored_password = user

            # Ensure stored password is correctly formatted before checking
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                session['user_id'] = user_id
                session.permanent = True  # Keep session active
                
                flash("Login successful!", "success")
                return redirect(url_for('upload.upload_file'))  # Redirect to the file upload page

        flash("Invalid email or password. Please try again.", "error")
        return redirect(url_for('auth.login'))

    return render_template('login.html', form=form)

# Logout Route
@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('auth.login'))
