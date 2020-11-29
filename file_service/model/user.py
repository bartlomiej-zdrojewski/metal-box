import json


class User:

    # TODO make separate class for address
    def __init__(self, id, login, password_hash, name, surname, birthdate, pesel, street,
                 apartment_number, city, country):
        self.id = id
        self.login = login
        self.password_hash = password_hash
        self.name = name
        self.surname = surname
        self.birthdate = birthdate
        self.pesel = pesel
        self.street = street
        self.apartment_number = apartment_number
        self.city = city
        self.country = country

    @classmethod
    def loadFromJson(cls, data):
        return cls(**data)

    def serialize(self):
        return json.dumps(self.__dict__)
