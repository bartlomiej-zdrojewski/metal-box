import json


class Package:

    # TODO make separate classes for person and address
    def __init__(self, id, creation_date, sender_name, sender_surname, sender_address,
                 sender_phone_number, receiver_name, receiver_surname, receiver_address,
                 receiver_phone_number):
        self.id = id
        self.creation_date = creation_date
        self.sender_name = sender_name
        self.sender_surname = sender_surname
        self.sender_address = sender_address
        self.sender_phone_number = sender_phone_number
        self.receiver_name = receiver_name
        self.receiver_surname = receiver_surname
        self.receiver_address = receiver_address
        self.receiver_phone_number = receiver_phone_number

    @classmethod
    def loadFromJson(cls, data):
        return cls(**data)

    def serialize(self):
        return json.dumps(self.__dict__)
