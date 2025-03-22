from flask import Blueprint, render_template, request, send_file, session, flash, redirect, url_for
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Prevent GUI issues
import matplotlib.pyplot as plt
from datetime import datetime
from backend.database import mysql

graphs_bp = Blueprint("graphs", __name__)

# Ensure the folder exists for saving graphs and uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), "static", "uploads")
GRAPH_FOLDER = os.path.join(os.getcwd(), "static", "graphs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GRAPH_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"csv", "xlsx", "txt"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_file(file_path):
    try:
        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            return pd.read_excel(file_path, engine="openpyxl")
        elif file_path.endswith(".txt"):
            return pd.read_csv(file_path, delimiter="\t")
        else:
            return None
    except Exception as e:
        print(f"⚠️ Error reading file {file_path}: {e}")
        return None

def generate_graph(file_path, graph_type):
    df = read_file(file_path)
    if df is None:
        return None

    df = df.dropna()
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) < 2:
        return None

    x_col, y_col = numeric_cols[:2]
    df = df[[x_col, y_col]].dropna()
    if df.empty:
        return None
    
    try:
        plt.figure(figsize=(8, 6))
        if graph_type == "line":
            plt.plot(df[x_col], df[y_col], marker='o', linestyle='-')
        elif graph_type == "bar":
            plt.bar(df[x_col], df[y_col])
        elif graph_type == "pie":
            if (df[y_col] > 0).all() and df[x_col].notnull().all():
                plt.pie(df[y_col], labels=df[x_col].astype(str), autopct='%1.1f%%')
            else:
                return None
        elif graph_type == "scatter":
            plt.scatter(df[x_col], df[y_col])
        elif graph_type == "histogram":
            plt.hist(df[x_col], bins=10, alpha=0.7)
        elif graph_type == "box":
            df[numeric_cols].boxplot()
        else:
            return None
        
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"{graph_type.replace('_', ' ').title()}")

        graph_filename = "visualized_graph.png"
        graph_path = os.path.join(GRAPH_FOLDER, graph_filename)
        plt.savefig(graph_path)
        plt.close()
        return graph_filename if os.path.exists(graph_path) else None
    except Exception as e:
        print(f"⚠️ Error generating graph: {e}")
        return None

@graphs_bp.route('/select_graph')
def select_graph():
    return render_template("select_graph.html")

@graphs_bp.route('/upload_file', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        flash("⚠️ Please log in first.", "error")
        return redirect(url_for('auth.login'))
    
    if 'file' not in request.files:
        flash("⚠️ No file part in request.", "error")
        return redirect(url_for('graphs.select_graph'))

    file = request.files['file']
    graph_type = request.form.get("graph_type")

    if file.filename == '' or not allowed_file(file.filename):
        flash("⚠️ Invalid file type or no file selected!", "error")
        return redirect(url_for('graphs.select_graph'))
    
    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO uploads (user_id, filepath, graph_type) VALUES (%s, %s, %s)",
                (session['user_id'], file_path, graph_type))
    mysql.connection.commit()
    cur.close()

    flash("✅ File uploaded successfully! Now generating the graph...", "success")
    return redirect(url_for('graphs.visualize'))

@graphs_bp.route('/visualize')
def visualize():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT filepath, graph_type FROM uploads ORDER BY id DESC LIMIT 1")
    file_info = cur.fetchone()
    cur.close()

    if not file_info:
        flash("⚠️ No file found. Upload a file first!", "error")
        return redirect(url_for('graphs.select_graph'))
    
    file_path, graph_type = file_info
    graph_filename = generate_graph(file_path, graph_type)

    if graph_filename:
        graph_url = url_for('static', filename=f'graphs/{graph_filename}')
        return render_template("dashboard.html", graph_path=graph_url, timestamp=datetime.now().timestamp())
    else:
        flash("⚠️ Unable to generate graph. Ensure your file has valid numerical data.", "error")
        return redirect(url_for('graphs.select_graph'))
@graphs_bp.route('/download')
def download_graph():
    graph_path = os.path.join(GRAPH_FOLDER, "visualized_graph.png")
    if os.path.exists(graph_path):
        return send_file(graph_path, as_attachment=True)
    else:
        flash("⚠️ No graph found to download!", "error")
        return redirect(url_for('graphs.visualize'))
