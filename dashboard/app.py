from flask import Flask, request, jsonify, session, render_template
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from auto_github_web import GitHubWebsiteCreator
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- Configuration ---
GITHUB_TOKEN = "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"
GITHUB_USERNAME = "foreignbandss"
GITHUB_REPO = "pages"
GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"

creator = GitHubWebsiteCreator(GITHUB_TOKEN, GITHUB_USERNAME)

# --- Routes ---
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/google_login', methods=['POST'])
def google_login():
    token = request.json.get("credential")
    try:
        idinfo = id_token.verify_oauth2_token(token, grequests.Request(), GOOGLE_CLIENT_ID)
        user_id = idinfo["sub"]
        session["user_id"] = user_id
        session["email"] = idinfo.get("email")
        return jsonify({"status": "success", "email": session["email"]})
    except ValueError:
        return jsonify({"status": "error"}), 400

@app.route('/save_project', methods=['POST'])
def save_project():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    project_name = data.get("folderName")
    files = data.get("files")  # list of {"name":..., "content":...}

    if not project_name or not files:
        return jsonify({"error": "Missing project name or files"}), 400

    user_folder = session["user_id"]
    project_folder = f"{user_folder}/{project_name}"

    try:
        creator.create_repo(GITHUB_REPO)
    except:
        pass

    urls = []
    for f in files:
        temp_path = f["name"]
        with open(temp_path, "w", encoding="utf-8") as tf:
            tf.write(f["content"])
        url = creator.create_folder_with_file(GITHUB_REPO, project_folder, temp_path)
        urls.append(url)
        os.remove(temp_path)

    return jsonify({"file_urls": urls})

@app.route('/list_projects', methods=['GET'])
def list_projects():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_folder = session["user_id"]
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{user_folder}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return jsonify({"projects": []})
    projects = [{"name": p["name"], "url": f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/tree/main/{user_folder}/{p['name']}"} for p in r.json()]
    return jsonify({"projects": projects})

if __name__ == "__main__":
    app.run(debug=True)
