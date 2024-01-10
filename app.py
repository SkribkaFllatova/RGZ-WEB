from flask import Flask, session, render_template, redirect, request, url_for
from Db import db
from Db.models import users, managers, transactions
from flask_migrate import Migrate


app = Flask(__name__)


app.secret_key = 'vlad'
user_db = "skribka"
host_ip = "127.0.0.1"
host_port = "5432"
database_name = "bank"
password = "filatova"


app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)


db.init_app(app)


@app.route('/')
def start():
    return redirect(url_for('login'))


@app.route("/app/index/", methods=['GET', 'POST'])
def main():
    if 'c_username' not in session and 'm_username' not in session:
        return redirect(url_for('login'))

    if 'c_username' in session:
        all_users = users.query.all()

        visible_user = session.get('c_full_name', 'Anon')

        return render_template('main.html', name=visible_user, all_users=all_users, balance=session.get('balance'), c_fullname=session.get('c_full_name'), phone=session.get('phone'), account_number=session.get('account_number'))
    
    if 'm_username' in session:
        all_managers = managers.query.all()

        visible_user = session.get('m_full_name', 'Anon')

        return render_template('main.html', name=visible_user, all_users=all_managers)
    
    return redirect('login.html')



@app.route('/app/loginAdm', methods=["GET", "POST"])
def loginAdm():
    errors = []

    if request.method == 'GET':
        return render_template("loginAdm.html", errors=errors)

    m_username = request.form.get("m_username")
    m_password = request.form.get("m_password")

    if not (m_username and m_password):
        errors.append("Пожалуйста, заполните все поля")
        return render_template("loginAdm.html", errors=errors)

    m_user = managers.query.filter_by(m_username=m_username).first()

    if m_user is None or m_user.m_password != m_password:
        errors.append('Неправильный пользователь или пароль')
        return render_template("loginAdm.html", errors=errors)

    session['m_id'] = m_user.manager_id
    session['m_username'] = m_user.m_username
    session['m_full_name'] = m_user.m_full_name

    return redirect("index")



@app.route('/app/login', methods=["GET", "POST"])
def login():
    errors = []

    if request.method == 'GET':
        return render_template("login.html", errors=errors)

    c_username = request.form.get("c_username")
    c_password = request.form.get("c_password")

    if not (c_username and c_password):
        errors.append("Пожалуйста, заполните все поля")
        return render_template("login.html", errors=errors)

    c_user = users.query.filter_by(c_username=c_username).first()

    if c_user is None or c_user.c_password != c_password:
        errors.append('Неправильный пользователь или пароль')
        return render_template("login.html", errors=errors)

    session['client_id'] = c_user.client_id
    session['c_username'] = c_user.c_username
    session['c_full_name'] = c_user.c_full_name
    session['balance'] = c_user.balance
    session['phone'] = c_user.phone
    session['account_number'] = c_user.account_number

    return redirect("index")


@app.route('/app/registerAdm', methods=['GET', 'POST'])
def registerAdm():
    errors = []

    if request.method == 'GET':
        return render_template("register.html", errors=errors)

    m_fullname = request.form.get("m_fullname")
    m_username = request.form.get("m_username")
    m_password = request.form.get("m_password")

    if not (m_fullname or m_username or m_password):
        errors.append("Пожалуйста, заполните все поля")
        print(errors)
        return render_template("register.html", errors=errors)

    existing_manager = managers.query.filter_by(m_username=m_username).first()

    if existing_manager:
        errors.append('Пользователь с данным именем уже существует')
        return render_template('register.html', errors=errors, resultСur=existing_manager)

    new_manager = managers(m_username=m_username, m_password=m_password, m_full_name=m_fullname)
    db.session.add(new_manager)
    db.session.commit()

    return redirect("/app/loginAdm")


@app.route('/app/register', methods=['GET', 'POST'])
def register():
    errors = []

    if request.method == 'GET':
        return render_template("register.html", errors=errors)

    c_fullname = request.form.get("c_fullname")
    c_username = request.form.get("c_username")
    c_password = request.form.get("c_password")
    phone = request.form.get("phone")
    account_number = request.form.get("account_number")
    balance = request.form.get("balance")

    if not (c_fullname or c_username or c_password or phone or account_number or balance):
        errors.append("Пожалуйста, заполните все поля")
        return render_template("register.html", errors=errors)

    existing_user = users.query.filter_by(c_username=c_username).first()
    existing_phone = users.query.filter_by(phone=phone).first()
    existing_an = users.query.filter_by(account_number=account_number).first()

    if existing_user:
        errors.append('Пользователь с данным именем уже существует')
        return render_template('register.html', errors=errors, resultСur=existing_user)
    
    if existing_phone:
        errors.append('Пользователь с данным номером телефона уже существует')
        return render_template('register.html', errors=errors, resultСur=existing_user)
    
    if existing_an:
        errors.append('Пользователь с данным номером счета уже существует')
        return render_template('register.html', errors=errors, resultСur=existing_user)

    new_user = users(c_username=c_username, c_password=c_password, c_full_name=c_fullname, phone=phone, account_number=account_number, balance=balance)
    db.session.add(new_user)
    db.session.commit()

    return redirect("/app/login")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Просмотр истории транзакций
@app.route('/transaction_history')
def transaction_history():
    if 'client_id' not in session:
        return redirect(url_for('login'))

    client_id = session['client_id']
    user = users.query.get(client_id)

    # Получение транзакций отправленных и полученных клиентом с информацией о пользователях
    transactions_info_sent = db.session.query(transactions, users.c_full_name.label('sender_full_name')).\
        join(users, transactions.sender_id == users.client_id).\
        filter(transactions.receiver_id == client_id).all()

    transactions_info_received = db.session.query(transactions, users.c_full_name.label('receiver_full_name')).\
        join(users, transactions.receiver_id == users.client_id).\
        filter(transactions.sender_id == client_id).all()

    return render_template('transaction_history.html', user=user, transactions_sent=transactions_info_sent, transactions_received=transactions_info_received)

# Перевод денег
@app.route('/transfer_money', methods=['POST', 'GET'])
def transfer_money():
    errors = []
    if 'client_id' not in session:
        return redirect(url_for('login'))

    client_id = session['client_id']
    user = users.query.get(client_id)

    if request.method == 'POST':
        receiver_type = request.form.get('receiver_type')
        receiver_id = request.form.get('receiver_id')
        amount = float(request.form.get('amount'))

        # Проверка наличия получателя и достаточности средств
        if receiver_type == 'phone':
            receiver = users.query.filter_by(phone=receiver_id).first()
        elif receiver_type == 'account_number':
            receiver = users.query.filter_by(account_number=receiver_id).first()
        else:
            return redirect(url_for('transfer_money'))

        if receiver and user.balance >= amount and receiver.client_id != client_id:
            # Создание транзакции
            new_transaction = transactions(amount=amount, sender_id=user.client_id, receiver_id=receiver.client_id)
            db.session.add(new_transaction)

            # Обновление балансов
            user.balance -= amount
            receiver.balance += amount

            db.session.commit()

            # Обновление баланса в сессии
            session['balance'] = user.balance

            return redirect(url_for('transaction_history'))
        else:
            errors.append('Нельзя отправить деньги себе')
            return render_template('transfer_money.html', errors=errors)
        
    return render_template('transfer_money.html', errors=errors)


@app.route('/all_users')
def all_users():
    if 'm_username' not in session:
        return redirect(url_for('login'))

    all_users = users.query.all()
    return render_template('all_users.html', all_users=all_users)


@app.route('/app/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = users.query.get(user_id)

    if request.method == 'POST':
        c_fullname = request.form.get("c_fullname")
        c_username = request.form.get("c_username")
        c_password = request.form.get("c_password")
        phone = request.form.get("phone")
        account_number = request.form.get("account_number")
        balance = request.form.get("balance")

        user.c_full_name = c_fullname
        user.c_username = c_username
        user.c_password = c_password
        user.phone = phone
        user.account_number = account_number
        user.balance = balance

        db.session.commit()

   
        return redirect(url_for('all_users'))

    return render_template('edit_user.html', user=user)


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'm_username' not in session:
        return redirect(url_for('login'))

    user = users.query.get(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('all_users'))
