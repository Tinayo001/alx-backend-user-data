#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import bcrypt
import uuid
from db import DB
from user import User
from sqlalchemy.orm.exc import NoResultFound


def _hash_password(password: str) -> bytes:
    """
    Hash a password.

    :param password: The password to hash.

    :return: The hashed password.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def _generate_uuid() -> str:
    """
    Generates uuids and returns its string representation
    """
    return str(uuid.uuid4())


class Auth:
    """
    Auth class to interact with the authentication database.
    """

    def __init__(self):
        """
        Constructor.
        """
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Register a user.

        Args:
            email: The email of the user.
            password: The password of the user.

        Returns:
            The user object.
        """
        if email is None or password is None:
            return None

        try:
            self._db.find_user_by(email=email)
        except NoResultFound:
            return self._db.add_user(email, _hash_password(password))
        else:
            raise ValueError("User {} already exists.".format(email))

    def valid_login(self, email: str, password: str) -> bool:
        """
        Validates users credentials for login
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False
        else:
            hashed_password = bcrypt.checkpw(
                    password.encode(), user.hashed_password)
            if hashed_password:
                return True
            return False

    def create_session(self, email: str) -> str:
        """
        Creates a session id for a user and stores it in the users table
        """
        if not email:
            return None

        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return None
        else:
            session_id = _generate_uuid()
            user.session_id = session_id
            return session_id

    def get_user_from_session_id(self, session_id: str) -> User:
        """
        Gets a user by their session id
        """
        if not session_id:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None
        return user

    def destroy_session(self, user_id: int) -> None:
        """
        Destroys a session for a user
        """
        try:
            user = self._db.find_user_by(id=user_id)
        except NoResultFound:
            return None
        else:
            user.session_id = None

    def get_reset_password_token(self, email: str) -> str:
        """
        Generates a reset password token and stores it in the users table
        """
        if not email:
            return None

        try:
            user = self._db.find_user_by(email=email)

        except NoResultFound:
            raise ValueError("User {} does not exist.".format(email))
        else:
            new_token = _generate_uuid()
            user.reset_token = new_token
            return new_token

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Updates a users password
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError
        else:
            hashed_password = _hash_password(password)
            user.hashed_password = hashed_password
            user.reset_token = None
