#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thur Nov  07 15:49:00 2024

@Author: Tinayo
"""
import re
from os import environ
import logging
import mysql.connector
from typing import List


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """
    Function to filter a message based on a list of fields

    Parameters
    ----------
    fields : list
        List of fields to filter
    redaction : str
        String to replace fields
    message : str
        String to filter
    separator : str
        String to separate fields

    Returns
    -------
    str
        Filtered message
    """
    for field in fields:
        message = re.sub(
            rf'({field})=([^{separator}]*)', rf'\1={redaction}', message)
    return message


def get_logger() -> logging.Logger:
    """
    Function to get logger
    """
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    stream_handler = logging.StreamHandler()
    formatter = RedactingFormatter(list(PII_FIELDS))
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Function to get database connection
    """
    username = environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    password = environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    host = environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = environ.get("PERSONAL_DATA_DB_NAME")

    mysql_connection = mysql.connector.connection.MySQLConnection(
            user=username,
            password=password,
            host=host,
            database=db_name
        )

    return mysql_connection


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """
        Constructor

        Parameters
        ----------
        fields : list
            List of fields to filter

        Returns
        -------
        None
        """
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a record

        Parameters
        ----------
        record : logging.LogRecord
            Record to format

        Returns
        -------
        str
            Formatted record
        """
        record.msg = filter_datum(self.fields, self.REDACTION,
                                  record.getMessage(), self.SEPARATOR)
        return super(RedactingFormatter, self).format(record)


def main():
    """
    Main function
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    field_names = [field[0] for field in cursor.description]

    logger = get_logger()

    for row in cursor:
        str_row = ''.join(f'{f}={str(r)}; ' for r, f in zip(row, field_names))
        logger.info(str_row.strip())

    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
