import re
import json


class Address:

    def __init__(self, street, building_number, apartment_number, postal_code,
                 city, country):
        self.street = street
        self.building_number = building_number
        self.apartment_number = apartment_number
        self.postal_code = postal_code
        self.city = city
        self.country = country

    @classmethod
    def __loadFromJson(cls, data):
        return cls(**data)

    @classmethod
    def loadFromData(cls, data):
        return Address.__loadFromJson(json.loads(data))

    def toData(self):
        return json.dumps(self.__dict__)

    def toString(self):
        return "{} {}/{}\n{} {}\n{}".format(
            self.street,
            self.building_number,
            self.apartment_number,
            self.postal_code,
            self.city,
            self.country
        )

    def validate(self):
        if not self.street:
            return "The street must not be empty."
        if not self.building_number:
            return "The building number must not be empty."
        if not self.apartment_number:
            return "The apartment number must not be empty."
        if not self.city:
            return "The city must not be empty."
        if not self.postal_code:
            return "the postal code must not be empty."
        if not self.country:
            return "The country must not be empty."
        if not re.search("^\d{2}-\d{3}$", self.postal_code):
            return "The postal code must match the XX-YYY format."
        return None
