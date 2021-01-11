import json


class Mailbox:

    def __init__(self, id, code, description):
        self.id = id
        self.code = code
        self.description = description

    @classmethod
    def __loadFromJson(cls, data):
        return cls(**data)

    @classmethod
    def loadFromData(cls, data):
        return Mailbox.__loadFromJson(json.loads(data))

    def toData(self):
        return json.dumps(self.__dict__)

    def validate(self):
        if not self.id:
            return "The ID must not be empty."
        if not self.code:
            return "The code must not be empty."
        if not self.description:
            return "The description must not be empty."
        return None
