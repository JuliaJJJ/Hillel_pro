import functools
import os
import time
from datetime import datetime, UTC

from flask import Flask, render_template, redirect, url_for, request, session

import database
import models
from dateutil import parser


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret_string")


def decorator_check_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("logged_in"):
            return func(*args, **kwargs)
        return redirect(url_for("user_login"))
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

    return redirect(url_for("user_login"))


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

    session["logged_in"] = True
    session["user_id"] = user.id
    return redirect(url_for("main_page"))


@app.route("/logout")
def user_logout():
    session.clear()
    return redirect(url_for("user_login"))


@app.route("/user/<int:user_id>", methods=["GET", "POST"])
def user_profile(user_id):
    user = database.db_session.get(models.User, user_id)
    if not user:
        return "User not found"

    if request.method == "POST":
        if session.get("user_id") != user_id:
            return "Forbidden"

        user.first_name = request.form["first_name"]
        user.last_name = request.form["last_name"]
        user.email = request.form["email"]
        user.password = request.form["password"]
        user.birth_date = parser.parse(
            request.form["birth_date"]
        ).date()

        database.db_session.commit()
        return redirect(url_for("user_profile", user_id=user_id))

    return render_template(
        "user_page.html",
        user=user,
        user_session=user
    )


@app.route("/user/<int:user_id>/delete")
def user_delete(user_id):
    if session.get("user_id") != user_id:
        return "Forbidden"

    user = database.db_session.get(models.User, user_id)
    if not user:
        return "User not found"

    database.db_session.delete(user)
    database.db_session.commit()
    session.clear()

    return redirect(url_for("user_login"))


@app.route("/films", methods=["GET"])
def films():
    query = database.db_session.query(models.Film)

    if request.args.get("name"):
        query = query.filter(
            models.Film.name.ilike(f"%{request.args['name']}%")
        )

    if request.args.get("year"):
        query = query.filter(
            models.Film.year == int(request.args["year"])
        )

    if request.args.get("rating"):
        query = query.filter(
            models.Film.rating == int(request.args["rating"])
        )

    if request.args.get("country"):
        query = query.filter(
            models.Film.country == request.args["country"]
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
    country = request.form.get("country")

    if not name:
        return "Film name required"

    film = models.Film(
        name=name,
        country=country,
        year=2025,
        rating=0,
        added_at=int(datetime.now(UTC).timestamp())
    )

    database.db_session.add(film)
    database.db_session.commit()

    return redirect(url_for("films"))


@app.route("/films/<int:film_id>", methods=["GET", "PUT", "DELETE"])
def film_detail(film_id):
    film = database.db_session.get(models.Film, film_id)
    if not film:
        return "Film not found"

    if request.method == "GET":
        actors = (
            database.db_session
            .query(models.Actor)
            .join(
                models.ActorFilm,
                models.Actor.id == models.ActorFilm.actor_id
            )
            .filter(models.ActorFilm.film_id == film_id)
            .all()
        )

        genres = (
            database.db_session
            .query(models.Genre)
            .join(
                models.GenreFilm,
                models.Genre.genre == models.GenreFilm.genre_id
            )
            .filter(models.GenreFilm.film_id == film_id)
            .all()
        )

        return render_template(
            "film.html",
            film=film,
            actors=actors,
            genres=genres
        )

    if request.method == "PUT":
        film.name = request.form.get("name", film.name)
        film.rating = request.form.get("rating", film.rating)
        database.db_session.commit()
        return "Film updated"

    database.db_session.delete(film)
    database.db_session.commit()
    return "Film deleted"


@app.route("/films/<int:film_id>/rating/<int:feedback_id>", methods=["PUT"])
def film_rating_update(film_id, feedback_id):
    feedback = (
        database.db_session
        .query(models.Feedback)
        .filter(
            models.Feedback.id == feedback_id,
            models.Feedback.film_id == film_id
        )
        .first()
    )

    if not feedback:
        return {"Feedback not found"}

    if "grade" in request.form:
        feedback.grade = int(request.form["grade"])

    if "description" in request.form:
        feedback.description = request.form["description"]

    database.db_session.commit()

    return {"Feedback updated"}


@app.route(
    "/films/<int:film_id>/rating/<int:feedback_id>",
    methods=["DELETE"]
)
def film_rating_delete(film_id, feedback_id):
    feedback = (
        database.db_session
        .query(models.Feedback)
        .filter(
            models.Feedback.id == feedback_id,
            models.Feedback.film_id == film_id
        )
        .first()
    )

    if not feedback:
        return {"Feedback not found"}

    database.db_session.delete(feedback)
    database.db_session.commit()

    return {"Feedback deleted"}


@app.route("/users/<int:user_id>/list", methods=["GET", "POST"])
def user_list(user_id):
    if request.method == "GET":
        lists = (
            database.db_session
            .query(models.List)
            .filter(models.List.user_id == user_id)
            .all()
        )
        return render_template(
            "user_lists.html",
            lists=lists,
            user_id=user_id
        )

    name = request.form.get("name")
    if not name:
        return "List name required"

    new_list = models.List(user_id=user_id, name=name)
    database.db_session.add(new_list)
    database.db_session.commit()

    return redirect(url_for("user_list", user_id=user_id))


@app.route("/users/<int:user_id>/list/<int:list_id>", methods=["GET", "POST"])
def user_list_item(user_id, list_id):
    user_list = (
        database.db_session
        .query(models.List)
        .filter_by(id=list_id, user_id=user_id)
        .first()
    )

    if not user_list:
        return "List not found"

    if request.method == "GET":
        films = (
            database.db_session
            .query(models.Film)
            .join(
                models.ListFilm,
                models.Film.id == models.ListFilm.film_id
            )
            .filter(models.ListFilm.list_id == list_id)
            .all()
        )

        return render_template(
            "user_list_items.html",
            list=user_list,
            films=films
        )

    film_id = request.form.get("film_id")
    if not film_id:
        return "Film ID required"

    exists = (
        database.db_session
        .query(models.ListFilm)
        .filter_by(list_id=list_id, film_id=film_id)
        .first()
    )

    if exists:
        return "Film already in list"

    database.db_session.add(
        models.ListFilm(list_id=list_id, film_id=film_id)
    )
    database.db_session.commit()

    return redirect(
        url_for("user_list_item", user_id=user_id, list_id=list_id)
    )


@app.route(
    "/users/<int:user_id>/list/<int:list_id>/<int:film_id>",
    methods=["DELETE"]
)
def user_list_item_delete(user_id, list_id, film_id):
    item = (
        database.db_session
        .query(models.ListFilm)
        .filter_by(list_id=list_id, film_id=film_id)
        .first()
    )

    if not item:
        return "Film not found in list"

    database.db_session.delete(item)
    database.db_session.commit()

    return "Film removed from list"


if __name__ == "__main__":
    app.run(debug=True)
