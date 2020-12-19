import re
import json
import os.path
from fpdf import FPDF
from dto.const import *
from dto.address import *
from dto.person import *


class Package:

    def __init__(self, id, serial_number, register_date,
                 image_file_path, document_file_path,
                 sender, sender_address, sender_phone_number,
                 receiver, receiver_address, receiver_phone_number,
                 status):
        self.id = id
        self.serial_number = serial_number
        self.register_date = register_date
        self.image_file_path = image_file_path
        self.document_file_path = document_file_path
        self.sender = sender
        self.sender_address = sender_address
        self.sender_phone_number = sender_phone_number
        self.receiver = receiver
        self.receiver_address = receiver_address
        self.receiver_phone_number = receiver_phone_number
        self.status = status

    @classmethod
    def __loadFromJson(cls, data):
        return cls(**data)

    @classmethod
    def loadFromData(cls, data):
        package_data = Package.__loadFromJson(json.loads(data))
        return Package(
            package_data.id,
            package_data.serial_number,
            package_data.register_date,
            package_data.image_file_path,
            package_data.document_file_path,
            Person.loadFromData(package_data.sender),
            Address.loadFromData(package_data.sender_address),
            package_data.sender_phone_number,
            Person.loadFromData(package_data.receiver),
            Address.loadFromData(package_data.receiver_address),
            package_data.receiver_phone_number,
            package_data.status
        )

    def toData(self):
        return json.dumps({
            "id": self.id,
            "serial_number": self.serial_number,
            "register_date": self.register_date,
            "image_file_path": self.image_file_path,
            "document_file_path": self.document_file_path,
            "sender": self.sender.toData(),
            "sender_address": self.sender_address.toData(),
            "sender_phone_number": self.sender_phone_number,
            "receiver": self.receiver.toData(),
            "receiver_address": self.receiver_address.toData(),
            "receiver_phone_number": self.receiver_phone_number,
            "status": self.status
        })

    def validate(self):
        if not self.id:
            return "ID must not be empty."
        if not self.serial_number:
            return "Serial number must not be empty."
        if not self.register_date:
            return "Register date must not be empty."
        if not self.image_file_path:
            return "Image file path must not be empty."
        if not self.sender:
            return "Sender's personal data must not be empty."
        if not self.sender_address:
            return "Sender's address must not be empty."
        if not self.sender_phone_number:
            return "Sender's phone number must not be empty."
        if not self.receiver:
            return "Receiver's personal data  must not be empty."
        if not self.receiver_address:
            return "Receiver's address must not be empty."
        if not self.receiver_phone_number:
            return "Receiver's phone number must not be empty."
        if not self.status:
            return "Status must not be empty."
        sender_validation_error = self.sender.validate(False)
        if sender_validation_error:
            return "Sender's personal data is invalid. " \
                "{}".format(sender_validation_error)
        sender_address_validation_error = self.sender.validate(False)
        if sender_address_validation_error:
            return "Sender's address data is invalid. " \
                "{}".format(sender_address_validation_error)
        if not re.search("^\d{9}$", self.sender_phone_number):
            return "Sender's phone number must consist of exactly 9 digits."
        receiver_validation_error = self.sender.validate(False)
        if receiver_validation_error:
            return "Receiver's personal data is invalid. " \
                "{}".format(receiver_validation_error)
        receiver_address_validation_error = self.sender.validate(False)
        if receiver_address_validation_error:
            return "Receiver's address data is invalid. " \
                "{}".format(receiver_address_validation_error)
        if not re.search("^\d{9}$", self.receiver_phone_number):
            return "Receiver's phone number must consist of exactly 9 digits."
        if self.status not in PACKAGE_STATUS_LIST:
            return "Status is invalid: {}.".format(self.status)
        return None

    def getStatusText(self):
        if self.status == PACKAGE_STATUS_NEW:
            return "Nowa"
        elif self.status == PACKAGE_STATUS_IN_MAILBOX:
            return "Oczekuje na odebranie z paczkomatu"
        elif self.status == PACKAGE_STATUS_RECEIVED_FROM_MAILBOX:
            return "Odebrana z paczkomatu"
        elif self.status == PACKAGE_STATUS_RECEIVED_FROM_SENDER:
            return "Odebrana od nadawcy"
        return "Nieznany status"

    def generateDocument(self):
        validation_error = self.validate()
        if validation_error:
            raise Exception(
                "Could not generate package document. Package is invalid. "
                "{}".format(validation_error))
        document_file_path = "{}package_{}.pdf".format(
            DOCUMENT_FILES_DIRECTORY, self.serial_number)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        self.__add_table_to_pdf(pdf)
        self.__add_image_to_pdf(pdf)
        pdf.output(document_file_path)
        if not os.path.isfile(document_file_path):
            raise Exception("Could not generate package document "
                            "(package_serial_number: {}). "
                            "Saving document file failed.").format(
                self.serial_number)
        self.document_file_path = document_file_path
        return document_file_path

    def __add_table_to_pdf(self, pdf):
        font_size = pdf.font_size
        column_width = 0.25 * (pdf.w - pdf.l_margin - pdf.r_margin)
        extended_colum_width = 2 * column_width
        row_height = 5 * font_size
        sender_text = "{}\n{}\ntel. {}".format(
            self.sender.toString(),
            self.sender_address.toString(),
            self.sender_phone_number)
        receiver_text = "{}\n{}\ntel. {}".format(
            self.receiver.toString(),
            self.receiver_address.toString(),
            self.receiver_phone_number)
        pdf.cell(column_width, row_height, "Numer seryjny", border=1)
        pdf.multi_cell(extended_colum_width, row_height,
                       self.serial_number, border=1)
        pdf.ln(0)
        pdf.cell(column_width, row_height, "Nadawca", border=1)
        pdf.multi_cell(extended_colum_width, font_size,
                       txt=sender_text, border=1)
        pdf.ln(0)
        pdf.cell(column_width, row_height, "Odbiorca", border=1)
        pdf.multi_cell(extended_colum_width, font_size,
                       txt=receiver_text, border=1)
        pdf.ln(1)

    def __add_image_to_pdf(self, pdf):
        if not os.path.isfile(self.image_file_path):
            raise Exception("Could not generate package document "
                            "(package_serial_number: {}). Image file "
                            "does not exist.").format(self.serial_number)
        image_width = 0.75 * (pdf.w - pdf.l_margin - pdf.r_margin)
        pdf.image(self.image_file_path, w=image_width)
        pdf.ln(1)
