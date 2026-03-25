from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sagar_file_share_secret"

UPLOAD_FOLDER = "uploads"
MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1 GB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def format_file_size(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def get_files():
    files = []
    for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.isfile(file_path):
            stat = os.stat(file_path)
            files.append({
                "name": filename,
                "size": format_file_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%d-%m-%Y %I:%M %p")
            })
    files.sort(key=lambda x: x["name"].lower())
    return files

@app.route("/")
def index():
    files = get_files()
    return render_template("index.html", files=files)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "files" not in request.files:
        flash("No files selected.")
        return redirect(url_for("index"))

    uploaded_files = request.files.getlist("files")
    uploaded_any = False

    for file in uploaded_files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            if filename:
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(save_path)
                uploaded_any = True

    if uploaded_any:
        flash("File uploaded successfully.")
    else:
        flash("Please choose at least one valid file.")

    return redirect(url_for("index"))

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

@app.route("/delete/<path:filename>", methods=["POST"])
def delete_file(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        flash(f"{filename} deleted successfully.")
    else:
        flash("File not found.")
    return redirect(url_for("index"))

@app.errorhandler(413)
def too_large(e):
    flash("File is too large. Maximum allowed size is 1 GB.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
