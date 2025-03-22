from flask import Flask, render_template, session, redirect, url_for
from backend import auth
from backend.database import init_db
from backend.upload import upload_bp  # Handles file uploads
from backend.graphs import graphs_bp  # Handles graph rendering
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure key

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists

# Initialize Database
init_db(app)

# Register Blueprints
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(upload_bp, url_prefix='/upload')
app.register_blueprint(graphs_bp, url_prefix='/graphs')

# ------------------- Routes -------------------

@app.route('/')
def index():
    """Redirects to the login page by default."""
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
def dashboard():
    """Displays the dashboard if user is logged in, otherwise redirects to login."""
    if 'user_id' in session:
        return render_template('dashboard.html')
    return redirect(url_for('auth.login'))

@app.route('/after_login')
def after_login():
    """Redirects user to graph selection page after login."""
    if 'user_id' in session:
        return redirect(url_for('graphs.select_graph'))  # Ensure this route exists in graphs.py
    return redirect(url_for('auth.login'))

@app.route('/logout')
def logout():
    """Logs out the user and redirects to login."""
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))

# ------------------- Error Handling -------------------

@app.errorhandler(404)
def page_not_found(error):
    """Handles 404 errors and renders a custom 404 page."""
    return render_template('404.html'), 404

# ------------------- Main -------------------

if __name__ == '__main__':
    app.run(debug=True)
