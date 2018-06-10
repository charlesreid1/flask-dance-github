import os, json
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, redirect, url_for, send_from_directory
from flask_dance.contrib.github import make_github_blueprint, github

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

app.config["RESULT_STATIC_PATH"] = os.getcwd()
app.config["GITHUB_OAUTH_CLIENT_ID"] = os.environ.get("GITHUB_OAUTH_CLIENT_ID")
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.environ.get("GITHUB_OAUTH_CLIENT_SECRET")
github_bp = make_github_blueprint(
                        client_id = os.environ.get('GITHUB_OAUTH_CLIENT_ID'),
                        client_secret = os.environ.get('GITHUB_OAUTH_CLIENT_SECRET'),
                        scope='read:org')
app.register_blueprint(github_bp, url_prefix="/login")

@app.route("/")
def index():
    if not github.authorized:
        return redirect(url_for("github.login"))

    username = github.get("/user").json()['login']
    target_org = 'microsoft'

    resp = github.get("/user/orgs")
    if resp.ok:

        all_orgs = resp.json()
        for org in all_orgs:
            if org['login']==target_org:
                return send_from_directory(os.getcwd(),'index.html')

if __name__ == "__main__":
    app.run()
