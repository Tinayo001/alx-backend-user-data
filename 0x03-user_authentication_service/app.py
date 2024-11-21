#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from auth import Auth
from sqlalchemy.orm.exc import NoResultFound
from flask import Flask, jsonify, request, abort, redirect, url_for


app = Flask(__name__)


AUTH = Auth()


@app.route('/', methods=['GET'], strict_slashes=False)
def index():
    """
    Returns the index page
    """
    return jsonify({"message": "Bienvenue"}), 200


@app.route('/users', methods=['POST'], strict_slashes=False)
def users():
    """
    Route to register a new user
    """
    try:
        email = request.form.get('email')
        password = request.form.get('password')

        user = AUTH.register_user(email, password)

        return jsonify({"email": "{}".format(user.email),
                        "message": "user created"}), 200
    except ValueError:
        return jsonify({"message": "email already registered"}), 400


@app.route('/sessions', methods=['POST'], strict_slashes=False)
def login():
    """
    Route to login a user
    """
    try:
        email = request.form.get('email')
        password = request.form.get('password')

        validate_login = AUTH.valid_login(email, password)

        if validate_login:
            session_id = AUTH.create_session(email)
            response_data = {
                    "email": email,
                    "message": "logged in"
                    }
            response = jsonify(response_data)

            response.set_cookie('session_id', value=session_id)

            return response, 200
        else:
            abort(401)
    except NoResultFound:
        abort(401)


@app.route('/sessions', methods=['DELETE'], strict_slashes=False)
def logout():
    """
    Route to logout a user
    """
    try:
        session_id = request.cookies.get('session_id')
        user = AUTH.get_user_from_session_id(session_id)

        if user:
            AUTH.destroy_session(user_id=user.id)
            return redirect(url_for('index'))
        else:
            abort(403)
    except NoResultFound:
        abort(403)


@app.route('/profile', methods=['GET'], strict_slashes=False)
def profile():
    """
    Route to get a user profile
    """
    try:
        session_id = request.cookies.get('session_id')

        if not session_id:
            abort(403)

        user = AUTH.get_user_from_session_id(session_id)

        if user:
            return jsonify({"email": user.email}), 200
        else:
            abort(403)
    except NoResultFound:
        abort(403)


@app.route('/reset_password', methods=['POST'], strict_slashes=False)
def get_reset_password_token():
    """
    Route to reset a password
    """
    email = request.form.get('email')

    if not email:
        abort(403)

    try:
        reset_token = AUTH.get_reset_password_token(email)
        return jsonify({"email": email, "reset_token": reset_token}), 200
    except Exception:
        abort(403)


@app.route('/reset_password', methods=['PUT'], strict_slashes=False)
def update_password():
    """
    Route to update a password
    """
    email = request.form.get('email')
    reset_token = request.form.get('reset_token')
    new_password = request.form.get('new_password')

    if not reset_token:
        abort(403)

    try:
        reset_password = AUTH.update_password(reset_token, new_password)
        return jsonify({"email": email, "message": "Password updated"}), 200
    except Exception:
        abort(403)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port="5000")
