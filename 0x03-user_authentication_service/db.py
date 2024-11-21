#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from user import Base
from user import User


class DB:
    """
    DB class
    """

    def __init__(self) -> None:
        """
        Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """
        Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Create and add a new user to the User table
        """
        if email is None or hashed_password is None:
            return None

        try:
            user = User(email=email, hashed_password=hashed_password)
            self._session.add(user)
            self._session.commit()
            return user
        except IntegrityError:
            self._session.rollback()
            return ValueError("User already exists")

    def find_user_by(self, **kwargs) -> User:
        """
        Find a user in the User table in the database
        """
        try:
            return self._session.query(User).filter_by(**kwargs).one()
        except NoResultFound as e:
            raise e
        except InvalidRequestError as error:
            raise error

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update a user in the User table in the database
        """
        if user_id is None or kwargs is None:
            return None

        user = self.find_user_by(id=user_id)

        for attr, value in kwargs.items():
            if not hasattr(user, attr):
                raise ValueError("Invalid attribute")
            setattr(user, attr, value)

        self._session.commit()
        return None
