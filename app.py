from flask import Flask, session, render_template, redirect, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from Db import db
from Db.models import users, managers


app = Flask(__name__)


app.secret_key = 'vlad'
user_db = "skribka"
host_ip = "127.0.0.1"
host_port = "5432"
database_name = "bank"
password = "filatova"


app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)


@app.route('/')
def start():
    return redirect(url_for('main'))


@app.route("/app/index/", methods=['GET', 'POST'])
def main():
    if 'name' not in session:
        return redirect(url_for('login'))

    all_users = users.query.all()

    visible_user = session.get('name', 'Anon')

    return render_template('index.html', name=visible_user, all_users=all_users)


@app.route('/app/login', methods=["GET", "POST"])
def loginPage():
    errors = []

    if request.method == 'GET':
        return render_template("login.html", errors=errors)

    username = request.form.get("username")
    password = request.form.get("password")

    if not (username or password):
        errors.append("Пожалуйста, заполните все поля")
        return render_template("login.html", errors=errors)

    user = users.query.filter_by(username=username).first()

    if user is None or not check_password_hash(user.password, password):
        errors.append('Неправильный пользователь или пароль')
        return render_template("login.html", errors=errors)

    session['name'] = user.name
    session['id'] = user.id
    session['username'] = user.username

    return redirect("index")
