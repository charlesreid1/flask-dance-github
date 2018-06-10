import os, json
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, redirect, url_for, send_from_directory
from flask_dance.contrib.github import make_github_blueprint, github

from os.path import join, isfile

# http://librelist.com/browser/flask/2012/2/22/flask-on-heroku-+-gunicorn-static-files/#109c5d714212f483bcbeecd778c879ad

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
STATIC_PATH = 'static_content'

app = Flask(__name__, 
            static_folder=os.path.join(PROJECT_ROOT,STATIC_PATH),
            static_url_path='')

app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

app.config["RESULT_STATIC_PATH"] = STATIC_PATH
app.config["GITHUB_OAUTH_CLIENT_ID"] = os.environ.get("GITHUB_OAUTH_CLIENT_ID")
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.environ.get("GITHUB_OAUTH_CLIENT_SECRET")
github_bp = make_github_blueprint(
                        client_id = os.environ.get('GITHUB_OAUTH_CLIENT_ID'),
                        client_secret = os.environ.get('GITHUB_OAUTH_CLIENT_SECRET'),
                        scope='read:org')
app.register_blueprint(github_bp, url_prefix="/login")

contents404 = "<html><body><h1>Status: Error 404 Page Not Found</h1></body></html>"
contents403 = "<html><body><h1>Status: Error 403 Access Denied</h1></body></html>"

# static files route
@app.route('/<path:path>')
def catch_all(path):

    if not github.authorized:
        return redirect(url_for("github.login"))

    username = github.get("/user").json()['login']
    target_org = 'microsoft'

    static_path = app.config["RESULT_STATIC_PATH"]
    resp = github.get("/user/orgs")
    if resp.ok:

        all_orgs = resp.json()
        for org in all_orgs:
            if org['login']==target_org:

                if(path==''):
                    return send_from_directory(static_path, 'index.html')

                elif(isdir(join(static_path,path))):
                    return send_from_directory(join(static_path,path),'index.html')

                elif(isfile(join(static_path,path))):
                    return send_from_directory(static_path, path)

                else:
                    return contents404

    return contents403

@app.errorhandler(404)
def error404(e):
    return contents404

if __name__ == "__main__":
    app.run()

