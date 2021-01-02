import re
import json
from datetime import datetime


class Person:

    def __init__(self, name, surname, birthdate="", pesel=""):
        self.name = name
        self.surname = surname
        self.birthdate = birthdate
        self.pesel = pesel

    @classmethod
    def __loadFromJson(cls, data):
        return cls(**data)

    @classmethod
    def loadFromData(cls, data):
        return Person.__loadFromJson(json.loads(data))

    def toData(self):
        return json.dumps(self.__dict__)

    def toString(self):
        return "{} {}".format(self.name, self.surname)

    def validate(self, strictMode=True):
        if not self.name:
            return "The name must not be empty."
        if not self.surname:
            return "The surname must not be empty."
        if strictMode:
            if not self.birthdate:
                return "The birthdate must not be empty."
            if not self.pesel:
                return "The PESEL must not be empty."
            if not re.search("^\d{4}-\d{2}-\d{2}$", self.birthdate):
                return "The birthdate must match the YYYY-MM-DD format."
            try:
                datetime.strptime(self.birthdate, '%Y-%m-%d')
            except ValueError:
                return "The birthdate must be a valid date."
            if not re.search("^[0-9]{11}$", self.pesel):
                return "The PESEL may only consist of exactly 11 digits."
            pesel_checksum = 0
            for i in range(len(self.pesel) - 1):
                digit = (int(self.pesel[i]) * ([1, 3, 7, 9])[i % 4]) % 10
                pesel_checksum += digit
            pesel_checksum = (10 - (pesel_checksum % 10)) % 10
            if int(self.pesel[10]) != pesel_checksum:
                return "The PESEL is invalid. Check digit is invalid " \
                    "({} vs {}).".format(self.pesel[10], pesel_checksum)
        return None
