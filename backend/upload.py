from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from werkzeug.utils import secure_filename
import os
from backend.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from backend.database import mysql
from backend.graphs import generate_graph  # Importing generate_graph function

upload_bp = Blueprint("upload", __name__)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files or request.files['file'].filename == '':
            flash('⚠️ No file selected. Please choose a file.', 'error')
            return redirect(request.url)

        file = request.files['file']
        graph_type = request.form.get('graph_type')

        if not graph_type:
            flash('⚠️ Please select a graph type.', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # Store file and graph info in database
            try:
                cur = mysql.connection.cursor()
                cur.execute(
                    "INSERT INTO uploads (filename, filepath, graph_type) VALUES (%s, %s, %s)", 
                    (filename, file_path, graph_type)
                )
                mysql.connection.commit()
                cur.close()
            except Exception as e:
                flash(f'⚠️ Database error: {e}', 'error')
                return redirect(request.url)

            # Generate graph
            graph_filename = generate_graph(file_path, graph_type)

            if graph_filename:
                flash('✅ File uploaded and graph generated successfully!', 'success')
                return redirect(url_for('graphs.visualize'))  # Redirect to visualization
            else:
                flash('⚠️ Graph generation failed. Ensure your file has valid numerical data.', 'error')
                return redirect(request.url)

    return render_template('select_graphs.html')
