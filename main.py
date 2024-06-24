import os
from datetime import timedelta

from flask import Flask, flash, request, redirect, url_for
from flask import jsonify
from flask_expects_json import expects_json
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from Operation import POSUtils
from POSActions import POSActions
from Schemas import station_create, user_create

app = Flask(__name__, static_folder='public', static_url_path='/static')

UPLOAD_FOLDER = './public'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
app.config['DEBUG'] = True
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)

jwt = JWTManager(app)


@app.route("/operator/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != "test" or password != "test":
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(
        identity={"username": username, "password": password, "user_type": "admin", "name": username})
    return jsonify(access_token=access_token)


@app.route("/login", methods=["POST"])
def login_main():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    login_data = POSActions.login(username, password)
    if login_data:
        print(login_data)
        access_token = create_access_token(identity=login_data)
        return jsonify(access_token=access_token)
    return jsonify({"msg": "Bad username or password"}), 401


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route("/ticket/sell", methods=["POST"])
@jwt_required()
def sell_tickets():
    current_user = get_jwt_identity()
    ticket_count = POSActions.sell_ticket(current_user.get("activation_id"), current_user.get("user_id"),
                                          request.json.get("qty"), request.json.get("ticket_id"))
    return jsonify(logged_in_as=current_user, ticket_count=ticket_count), 200


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"ping": "pong"}), 201


@app.route("/ticket/prices", methods=["GET"])
def get_prices():
    station_id = POSUtils.get_ticket_prices()
    if station_id:
        return jsonify({"data": station_id}), 201
    return jsonify(id=station_id), 409


@app.route("/station/create", methods=["POST"])
@jwt_required()
@expects_json(station_create)
def station_create():
    station_id = POSUtils.create_station(request.json.get("name"))
    if station_id:
        return jsonify({"msg": "Station created successfully", "station_id": station_id}), 201
    return jsonify(id=station_id), 409


@app.route("/station/activate", methods=["POST"])
@jwt_required()
@expects_json(station_create)
def station_activate():
    station_id = POSUtils.create_station(request.json.get("name"))
    if station_id:
        return jsonify({"msg": "Station created successfully", "station_id": station_id}), 201
    return jsonify(id=station_id), 409


@app.route("/user/create", methods=["POST"])
@jwt_required()
@expects_json(user_create)
def user_create():
    user_id = POSUtils.create_user(request.json.get("username"), request.json.get("password"),
                                   request.json.get("user_type"))
    if user_id:
        return jsonify({"msg": "Station created successfully", "user_id": user_id}), 201
    return jsonify(id=user_id), 409


@app.route("/user/list", methods=["GET"])
def get_user_list():
    return jsonify(data=POSUtils.get_user_list()), 200


@app.route("/activation/list", methods=["GET"])
def get_activation_list():
    return jsonify(data=POSUtils.get_activation_list()), 200


@app.route("/report/user/<user_id>", methods=["GET"])
def get_user_report(user_id):
    return jsonify(data=POSUtils.get_report_by_user(user_id)), 200


@app.route("/report/<report_type>", methods=["GET"])
def get_users_report(report_type):
    print(request.remote_addr)
    return jsonify(data=POSUtils.report_handler(int(report_type))), 200


@app.route("/print/report/<series>", methods=["GET"])
def update_print_count(series):
    return jsonify(data=POSUtils.print_ack(int(series))), 200


@app.route("/print/report/failed/<user_id>", methods=["GET"])
def get_print_failed(user_id):
    return jsonify(data=POSUtils.get_failed_prints(user_id)), 200


@app.route("/report/dates", methods=["GET"])
def get_report_dates():
    return jsonify(data=POSUtils.get_report_dates()), 200


@app.route("/print/report/failed/count/<user_id>", methods=["GET"])
def get_print_failed_count(user_id):
    return jsonify(data=POSUtils.get_failed_prints_count(user_id)), 200


@app.route("/price/<price_id>", methods=["PUT"])
# @jwt_required()
def price_update(price_id):
    price = POSUtils.price_update(dict(request.json))
    if price:
        return jsonify({"msg": "Station created successfully", "user_id": price_id}), 201
    return jsonify(id=price_id), 409


@app.route("/activation/<activation_id>/<activation_type>", methods=["PUT"])
def update_activation(activation_id, activation_type):
    price = POSUtils.set_activation(activation_id, activation_type)
    if price:
        return jsonify({"msg": "Station created successfully", "activation_id": activation_id}), 201
    return jsonify(id=activation_id), 409


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route("/users/activations", methods=["GET"])
def get_activation_list_():
    return jsonify(data=POSUtils.get_activation_list()), 200


@app.route("/users/activation/<activation_id>", methods=["PUT"])
def set_activation(activation_id):
    return jsonify(data=POSUtils.get_user_list()), 200


@app.route("/users/activation/<activation_id>", methods=["GET"])
def set_activation_all(activation_id):
    return jsonify(data=POSUtils.set_activation_all(activation_id)), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
