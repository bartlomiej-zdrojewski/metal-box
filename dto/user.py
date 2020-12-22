import json
from dto.address import *
from dto.person import *


class User:

    def __init__(self, id, login, password_hash, person, address, is_courier):
        self.id = id
        self.login = login
        self.password_hash = password_hash
        self.person = person
        self.address = address
        self.is_courier = is_courier

    @classmethod
    def __loadFromJson(cls, data):
        return cls(**data)

    @classmethod
    def loadFromData(cls, data):
        user_data = User.__loadFromJson(json.loads(data))
        return User(
            user_data.id,
            user_data.login,
            user_data.password_hash,
            Person.loadFromData(user_data.person),
            Address.loadFromData(user_data.address),
            user_data.is_courier
        )

    def toData(self):
        return json.dumps({
            "id": self.id,
            "login": self.login,
            "password_hash": self.password_hash,
            "person": self.person.toData(),
            "address": self.address.toData(),
            "is_courier": self.is_courier
        })

    def validate(self, strictMode=True):
        if not self.id:
            return "ID must not be empty."
        if not self.login:
            return "Login must not be empty."
        if not self.password_hash:
            return "Password hash must not be empty."
        if not self.person:
            return "Personal data must not be empty."
        if not self.address:
            return "Address data must not be empty."
        if type(self.is_courier) is not bool:
            return "The \"is_courier\" flag is invalid."
        if self.is_courier:
            person_validation_error = self.person.validate(False)
            if person_validation_error:
                return "Personal data is invalid. " + person_validation_error
        else:
            person_validation_error = self.person.validate(strictMode)
            if person_validation_error:
                return "Personal data is invalid. " + person_validation_error
            address_validation_error = self.address.validate()
            if address_validation_error:
                return "Address data is invalid. " + address_validation_error
        return None

    def isCourer(self):
        if type(self.is_courier) is not bool:
            raise Exception("The \"is_courier\" flag is invalid.")
        return self.is_courier
