from flask import Flask

app = Flask(__name__)

@app.route("/")
def main_page():
    return 'Hello, World!'


@app.route('/register',methods=['POST'])
def user_register():
    return 'Register'


@app.post('/login')
def user_login():
    return 'Login'


@app.post('/logout',methods=['GET'])
def user_logout():
    return 'Logout'


@app.route('/user/<user_id>',methods=['GET', 'PATCH'])
def user_profile(user_id):
    return f'User {user_id}'


app.route('/user/<user_id>',methods=['DELETE'])
def user_delete(user_id):
    return f'User {user_id} deleted'


@app.route('/films',methods=['GET'])
def films():
    return 'Films'


@app.route('/films',methods=['POST'])
def film_add():
    return 'Film added'

@app.route('/films/<film_id>',methods=['GET'])
def film_info(film_id):
    return f'Film {film_id}'


@app.route('/films/<film_id>',methods=['PUT'])
def film_update(film_id):
    return f'Film {film_id} updated'


@app.route('/films/<film_id>, methods=['DELETE'])
def film_delete(film_id):
    return f'Film {film_id} deleted'


@app.route('/films/<film_id>/rating', methods=['POST])
def film_rating(film_id):
    return f'Film{film_id} rated'


@app.route('/films/<film_id>/rating', methods=['GET])
def film_rating_info(film_id):
    return f'Film{film_id} rating'


@app.route('/films/<film_id>/rating', methods=['DELETE'])
def film_rating_delete(film_id, feedback_id):
    return f'Film {film_id} rating {feedback_id} deleted'


@app.route('/films/<film_id>/rating/<feedback_id>/feedback_id', methods=['PUT'])
def film_rating_update(film_id, feedback_id):
    return f'Film {film_id} rating {feedback_id} updated'


@app.route('/films/<film_id>/rating/<feedback_id>/feedback_id', methods=['GET'])
def film_rating_feedback(film_id, feedback_id):
    return f'Film {film_id} rating {feedback_id} feedback'


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
    app.run()