import os
from datetime import datetime, UTC
from functools import wraps

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
)

from dateutil import parser

import database
import models

from tasks import send_confirmation_email


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret_string")


def decorator_check_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("user_login"))
        return func(*args, **kwargs)
    return wrapper


@app.route("/")
@decorator_check_login
def main_page():
    films = (
        database.db_session
        .query(models.Film)
        .order_by(models.Film.added_at.desc())
        .limit(10)
        .all()
    )
    return render_template("main_page.html", films=films)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    user = models.User(
        first_name=request.form.get("fname"),
        last_name=request.form.get("lname"),
        login=request.form.get("login"),
        email=request.form.get("email"),
        password=request.form.get("password"),
        birth_date=parser.parse(
            request.form.get("birth_date")
        ).date()
    )

    database.db_session.add(user)
    database.db_session.commit()


    send_confirmation_email.delay(user.email)

    return redirect(url_for("user_login"))


@app.route("/send-test-email")
def send_test_email():
    send_confirmation_email.delay("test@example.com")
    return {"status": "email task sent"}


@app.route("/login", methods=["GET"])
def user_login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def user_login_post():
    user = (
        database.db_session
        .query(models.User)
        .filter(
            models.User.login == request.form["login"],
            models.User.password == request.form["password"]
        )
        .first()
    )

    if not user:
        return "Login failed"

    session["user_id"] = user.id
    return redirect(url_for("main_page"))


@app.route("/logout")
def user_logout():
    session.clear()
    return redirect(url_for("user_login"))


@app.route("/films", methods=["GET"])
def films():
    query = database.db_session.query(models.Film)

    if request.args.get("name"):
        query = query.filter(
            models.Film.name.ilike(f"%{request.args['name']}%")
        )

    films = query.all()
    countries = database.db_session.query(models.Country).all()

    return render_template(
        "films.html",
        film=films,
        countries=countries
    )


@app.route("/films", methods=["POST"])
def film_create():
    name = request.form.get("name")

    if not name:
        return "Film name required"

    film = models.Film(
        name=name,
        country=request.form.get("country"),
        year=2025,
        rating=0,
        added_at=int(datetime.now(UTC).timestamp())
    )

    database.db_session.add(film)
    database.db_session.commit()

    return redirect(url_for("films"))


@app.route("/films/<int:film_id>")
@decorator_check_login
def film_details(film_id):
    film = (
        database.db_session
        .query(models.Film)
        .filter(models.Film.id == film_id)
        .first()
    )

    if not film:
        return "Film not found"


    actors = getattr(film, "actors", [])
    genres = getattr(film, "genres", [])

    return render_template(
        "film.html",
        film=film,
        actors=actors,
        genres=genres
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)