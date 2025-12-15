import functools
import os
import database


from flask import Flask, render_template,redirect,url_for
from flask import request,session
from flask import redirect
from flask import url_for
from models import User

from sqlalchemy import select
from dateutil import parser
import sqlite3

import models

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.secret_key = os.environ.get('SECRET_KEY', 'secret string')

def film_dictionary(cursor,row):
    d={}
    for idx,col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class db_connection:
    def __init__(self):
        self.conn=sqlite3.connect('database.db')
        self.conn.row_factory = film_dictionary
        self.cur = self.conn.cursor()


    def __enter__(self):
        return self.cur


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()




def get_db_result(query):
    conn = sqlite3.connect('database.db', timeout=5)
    conn.row_factory = film_dictionary
    cur = conn.cursor()
    res = cur.execute(query)
    result = res.fetchall()
    conn.close()
    return result


def decorator_check_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'login_in' in session:
            return func (*args, **kwargs)
        else:
            return redirect(url_for('user_login'))
    return wrapper

@app.route("/")
@decorator_check_login
def main_page():
    with db_connection() as cur:
        result = cur.execute('SELECT id,poster,name FROM film order by added_at desc limit 10').fetchall()

    #result = get_db_result('SELECT id,poster,name FROM film order by added_at desc limit 10')
    return render_template('main_page.html', films=result)


@app.route('/register',methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def user_register():
    first_name = request.form['fname']
    last_name = request.form['lname']
    password = request.form['password']
    login = request.form['login']
    email = request.form['email']
    birth_date = parser.parse(request.form['birth_date'])

    database.init_db()
    new_user = models.User(first_name=first_name, last_name=last_name, password=password, login=login, email=email, birth_date=birth_date)
    database.db_session.add(new_user)
    database.db_session.commit()

    return 'Registered'



@app.route('/login', methods=['GET'])
def user_login():
    return  render_template('login.html')



@app.route('/login', methods=['POST'])
def user_login_post():
    login = request.form['login']
    password = request.form['password']


    database.init_db()
    stmt = select(User).where(User.login == login, models.User.password == password)
    data = database.db_session.execute(stmt).fetchall()

    result = database.db_session.query(models.User).filter_by(login=login, password=password).first()

    if result:
        session['logged_in']= True
        session['user_id'] = result.id
        return f'login with user {result.login}(id={result.id})'
    return 'Login failed'


@app.route('/logout', methods=['GET'])
@decorator_check_login
def user_logout():
    session.clear()
    return 'Logout'


@app.route('/user/<user_id>',methods=['GET', 'POST'])

def user_profile(user_id):
    session_user_id = session.get('user_id')
    if request.method == 'POST':

        if int(user_id) !=session_user_id:
            return 'You can edit only your profile'

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        birth_date = request.form['birth_date']
        phone_number = request.form['phone_number']
        photo =request.form['photo']
        additional_info =request.form['additional_info']
        with db_connection() as cur:
            cur.execute(
                f"UPDATE user SET first_name='{{first_name}}', last_name='{{last_name}}', email='{{email}}', password='{{password}}', birth_date='{{birth_date}}', phone='{{phone}}', photo='{{photo}}', additional_info='{{additional_info}}' WHERE id={{user_id}}")
        return f'User{user_id} updated'

    else:
        with db_connection() as cur:
            cur.execute(f'SELECT * FROM user WHERE id={user_id}')
            user_by_id = cur.fetchone()
            if session_user_id is None:
               user_by_session = 'No user in session'

            else:
                cur.execute(f'SELECT * FROM user WHERE id={session_user_id}')
                user_by_session = cur.fetchone()
        return render_template('user_page.html', user=user_by_id, user_session= user_by_session)
    # return f'You logged in as {user_by_session}, user {user_id} data: {user_by_id}'


@app.route('/user/<user_id>/delete', methods=['GET'])
def user_delete(user_id):
    session_user_id = session.get('user_id')
    if user_id ==session_user_id:
        return f'User {user_id} deleted'
    else:
        return 'You can delete only your profile'



@app.route('/films', methods=['GET'])
def films():
    filter_params = request.args
    filter_list_texts =[]
    for key, value in filter_params.items():
        if value:
            if key == 'name':
                filter_list_texts.append(f"name like '%{value}%")
            else:
                filter_list_texts.append(f"{key}='{value}'")
    additional_filter =''
    if filter_params:
            additional_filter = 'where' + 'and'.join(filter_list_texts)
    result = get_db_result(f'SELECT * FROM film order by added_at desc')
    countries =get_db_result("select * from country")
    return render_template('films.html', film = result, countries = countries)


@app.route('/films', methods=['POST'])
def film_add():

    return 'Film added'

@app.route('/films/<film_id>', methods=['GET'])
def film_info(film_id):
    with db_connection() as cur:
        result =cur.execute('SELECT * FROM film WHERE id = ?', (film_id,)).fetchall()
        actors =cur.execute(f'SELECT * FROM actor join actor_film on actor.id == actor_film.actor_id where actor_film.film_id = {film_id}')
        genres = cur.execute(f'SELECT * FROM genre_film where film_id = {film_id}').fetchall()


    return f'Film {film_id} is {result}, actors: {actors}, genres: {genres}'




@app.route('/films/<film_id>', methods=['PUT'])
def film_update(film_id):
    return f'Film {film_id} updated'


@app.route('/films/<film_id>', methods=['DELETE'])
def film_delete(film_id):
    return f'Film {film_id} deleted'


@app.route('/films/<film_id>/rating', methods=['POST'])
def film_rating(film_id):
    return f'Film{film_id} rated'


@app.route('/films/<film_id>/rating', methods=['GET'])
def film_rating_info(film_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    ratingRow = cur.execute(
        f'SELECT rating FROM film WHERE id = {film_id}').fetchone()
    return f'Film{ratingRow[0]} rating'


@app.route('/films/<film_id>/rating', methods=['DELETE'])
def film_rating_delete(film_id, feedback_id):
    return f'Film {film_id} rating {feedback_id} deleted'


@app.route('/films/<film_id>/rating/<feedback_id>/feedback_id', methods=['PUT'])
def film_rating_update(film_id, feedback_id):
    return f'Film {film_id} rating {feedback_id} updated'


@app.route('/films/<film_id>/rating/<feedback_id>/feedback', methods=['GET'])
def film_rating_feedback(film_id, feedback_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    feedbackRow = cur.execute(
        f'SELECT * FROM feedback WHERE id = {feedback_id} AND film = {film_id}').fetchone()
    return f'Film {feedbackRow}'


@app.route('/users/<user_id>/list', methods=['GET', 'POST'])
def user_list(user_id):
    return f'User {user_id} list'


@app.route('/users/<user_id>/list', methods=['DELETE'])
def user_list_delete(user_id):
    return f'User {user_id} list deleted'


@app.route('/users/<user_id>/list/<list_id>', methods=['GET', 'POST'])
def user_list_item(user_id, list_id):
    return f'User {user_id} list item {list_id}'


@app.route('/users/<user_id>/list/<list_id>/<film_id>', methods=['DELETE'])
def user_list_item_delete(user_id, list_id, film_id):
    return f'User {user_id} list item {list_id} deleted'





if __name__ == '__main__':
    app.run(debug=False)