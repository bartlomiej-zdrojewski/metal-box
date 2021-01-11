# TODO move mailbox related endpoints to mailbox service?

import math
import os
from flask import Flask, request, jsonify, send_file, abort
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS, cross_origin
from flask_restplus import Api, Resource, fields
from flask_socketio import SocketIO, join_room, leave_room, emit
from db.dbi import *

app = Flask(__name__, static_url_path="")
app.config["JWT_SECRET_KEY"] = os.environ.get(JWT_SECRET_KEY)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = SESSION_EXPIRATION_TIME
jwt = JWTManager(app)
api = Api(app)
socket_io = SocketIO(app, cors_allowed_origins=[
    MAIN_SERVICE_ORIGIN,
    COURIER_SERVICE_ORIGIN,
    MAILBOX_SERVICE_ORIGIN])
dbi = DatabaseInterface()

CORS(app, origins=[
    MAIN_SERVICE_ORIGIN,
    COURIER_SERVICE_ORIGIN,
    MAILBOX_SERVICE_ORIGIN],
    allow_headers=["Authorization"])

package_namespace = api.namespace(
    "Package",
    path="/api/package",
    description="Package Service API")

mailbox_namespace = api.namespace(
    "Mailbox",
    path="/api/mailbox",
    description="Mailbox Service API")

# TODO use socket_io.run(app)? will https still work?


#
# PACKAGE NAMESPACE
#


@package_namespace.route("")
class PackageListResource(Resource):

    create_package_form_model = api.model("Create a Package Form Model", {
        "sender_name": fields.String(
            required=True, description="A sender's name."),
        "sender_surname": fields.String(
            required=True, description="A sender's surname."),
        "sender_street": fields.String(
            required=True, description="A sender's street name (a part of "
            "the address)."),
        "sender_building_number": fields.String(
            required=True, description="A sender's building number (a part of "
            "the address)."),
        "sender_apartment_number": fields.String(
            required=True, description="A sender's apartment number (a part of "
            "the address)."),
        "sender_postal_code": fields.String(
            required=True, description="A sender's postal code (a part of "
            "the address)."),
        "sender_city": fields.String(
            required=True, description="A sender's city (a part of "
            "the address)."),
        "sender_country": fields.String(
            required=True, description="A sender's country (a part of "
            "the address)."),
        "sender_phone_number": fields.String(
            required=True, description="A sender's phone number."),
        "receiver_name": fields.String(
            required=True, description="A receiver's name."),
        "receiver_surname": fields.String(
            required=True, description="A receiver's surname."),
        "receiver_street": fields.String(
            required=True, description="A receiver's street name (a part of "
            "the address)."),
        "receiver_building_number": fields.String(
            required=True, description="A receiver's building number (a part "
            "of the address)."),
        "receiver_apartment_number": fields.String(
            required=True, description="A receiver's apartment number (a part "
            "of the address)."),
        "receiver_postal_code": fields.String(
            required=True, description="A receiver's postal code (a part of "
            "the address)."),
        "receiver_city": fields.String(
            required=True, description="A receiver's city (a part of "
            "the address)."),
        "receiver_country": fields.String(
            required=True, description="A receiver's country (a part of "
            "the address)."),
        "receiver_phone_number": fields.String(
            required=True, description="A receiver's phone number."),
        "image": fields.String(
            required=True, description="A package photo. A PNG or JPEG file.")})

    @jwt_required
    @cross_origin()
    @api.param("page_index", "An index of the page. Starts with 0.",
               type=int, default=0)
    @api.param("page_size", "A page size. When 0 is given, all packages are "
               "listed.",
               type=int, default=5)
    @api.param("as_courier", "A flag determininig whether packages assigned to "
               "the courier (true) or regular user's packages (false) should "
               "be listed. If true, the user must be a courier.",
               type=bool, default=False)
    @api.doc(responses={200: "OK",
                        400: "Bad Request, {error_message: string}"})
    def get(self):
        """ Returns a list of packages. """
        login = get_jwt_identity()
        as_courier = False
        if request.args.get("as_courier", "false") == "true":
            if not dbi.isUserCourier(login):
                return jsonify(error_message="The user is not a courier "
                               "(login: {}).".format(login)), 400
            as_courier = True
        page_index = request.args.get("page_index", 0, int)
        page_size = request.args.get("page_size", 5, int)
        return self.__fetchPackageList(
            login, page_index, page_size, as_courier), 200

    @jwt_required
    @cross_origin()
    @api.expect(create_package_form_model)
    @api.doc(responses={201: "Created",
                        400: "Bad Request, {error_message: string}"})
    def post(self):
        """ Creates a new package. """
        request_error = self.__validatePackageRegisterRequest(request)
        if request_error:
            return jsonify(error_message=request_error), 400
        login = get_jwt_identity()
        self.__registerPackageFromRequest(login, request)
        return "Created", 201

    def __fetchPackageList(self, user_login, page_index, page_size, as_courier):
        if not dbi.doesUserExist(user_login):
            abort(500,
                  "Could not fetch the package list. The user does not exists "
                  "(user_login: {}).".format(user_login))
        source_map_key = PACKAGE_ID_TO_SENDER_ID_MAP
        if as_courier:
            if not dbi.isUserCourier(user_login):
                abort(500,
                      "Could not fetch the package list. The user is not "
                      "a courier (user_login: {})".format(user_login))
            source_map_key = PACKAGE_ID_TO_COURIER_ID_MAP
        package_list = []
        user_id = dbi.getUserIdFromLogin(user_login)
        for package_id in dbi.getDatabase().hkeys(source_map_key):
            if user_id == dbi.getDatabase().hget(source_map_key, package_id):
                if not dbi.getDatabase().exists(package_id):
                    abort(500,
                          "Could not fetch the package list. One of the "
                          "packages does not exist (package_id: "
                          "{}).".format(package_id))
                package = Package.loadFromData(
                    dbi.getDatabase().get(package_id))
                package_register_date = dateutil.parser.parse(
                    package.register_date)
                package_register_date_text = package_register_date.strftime(
                    "%Y-%m-%d %H:%M:%S")
                package_list.append({
                    "serial_number": package.serial_number,
                    "register_date": package_register_date_text,
                    "status": package.status,
                    "status_text": package.getStatusText(),
                    "url": PACKAGE_SERVICE_API_URL + "/package/" +
                    package.serial_number})
                if as_courier:
                    package_is_deletable = "false"
                    if package.status == PACKAGE_STATUS_NEW:
                        package_is_deletable = "true"
                    package_list[-1]["is_deletable"] = package_is_deletable
        return self.__generatePackageListPage(package_list, page_index,
                                              page_size, as_courier)

    def __generatePackageListPage(self, package_list, page_index, page_size,
                                  as_courier):
        if not page_index:
            page_index = 0
        if not page_size:
            page_size = 0
        if page_size > 0:
            first_page = 0
            last_page = int(math.floor(len(package_list) / page_size))
            if (last_page * page_size) == len(package_list):
                last_page = last_page - 1
            if last_page < 0:
                last_page = 0
            if page_index < first_page:
                page_index = first_page
            if page_index > last_page:
                page_index = last_page
            list_begin = page_index * page_size
            list_end = list_begin + page_size
            if list_end >= len(package_list):
                list_end = len(package_list)
            page_object = {
                "page_index": page_index,
                "page_size": page_size,
                "page_count": last_page + 1,
                "package_list": package_list[list_begin:list_end],
                "package_count": len(package_list)
            }
            url_prefix = PACKAGE_SERVICE_API_URL + "/package"
            url_courier_sufix = ""
            if as_courier:
                url_courier_sufix = "&as_courier=true"
            if page_index != first_page:
                page_object["first_page"] = first_page
                page_object["first_page_url"] = \
                    url_prefix + "?page_index={}&page_size={}{}".format(
                        page_object["first_page"], page_size,
                        url_courier_sufix)
                page_object["previous_page"] = page_index - 1
                page_object["previous_page_url"] = \
                    url_prefix + "?page_index={}&page_size={}{}".format(
                        page_object["previous_page"], page_size,
                        url_courier_sufix)
            if page_index != last_page:
                page_object["next_page"] = page_index + 1
                page_object["next_page_url"] = \
                    url_prefix + "?page_index={}&page_size={}{}".format(
                        page_object["next_page"], page_size,
                        url_courier_sufix)
                page_object["last_page"] = last_page
                page_object["last_page_url"] = \
                    url_prefix + "?page_index={}&page_size={}{}".format(
                        page_object["last_page"], page_size,
                        url_courier_sufix)
            return page_object
        else:
            return {
                "page_index": 0,
                "page_size": len(package_list),
                "page_count": 1,
                "package_list": package_list,
                "package_count": len(package_list)}

    def __validatePackageRegisterRequest(self, request):
        sender = Person(
            request.form.get("sender_name"),
            request.form.get("sender_surname"))
        sender_validation_error = sender.validate(False)
        if sender_validation_error:
            return "The sender's personal data is invalid. " \
                "{}".format(sender_validation_error)
        sender_address = Address(
            request.form.get("sender_street"),
            request.form.get("sender_building_number"),
            request.form.get("sender_apartment_number"),
            request.form.get("sender_postal_code"),
            request.form.get("sender_city"),
            request.form.get("sender_country"))
        sender_address_validation_error = sender_address.validate()
        if sender_address_validation_error:
            return "The sender's address data is invalid. " \
                "{}".format(sender_address_validation_error)
        sender_phone_number = request.form.get("sender_phone_number")
        if not sender_phone_number:
            return "The sender's phone number must not be empty."
        if not re.search("^\d{9}$", sender_phone_number):
            return "The sender's phone number must consist of exactly 9 digits."
        receiver = Person(
            request.form.get("receiver_name"),
            request.form.get("receiver_surname"))
        receiver_validation_error = receiver.validate(False)
        if receiver_validation_error:
            return "The receiver's personal data is invalid. " \
                "{}".format(receiver_validation_error)
        receiver_address = Address(
            request.form.get("receiver_street"),
            request.form.get("receiver_building_number"),
            request.form.get("receiver_apartment_number"),
            request.form.get("receiver_postal_code"),
            request.form.get("receiver_city"),
            request.form.get("receiver_country"))
        receiver_address_validation_error = receiver_address.validate()
        if receiver_address_validation_error:
            return "The receiver's address data is invalid. " \
                "{}".format(receiver_address_validation_error)
        receiver_phone_number = request.form.get("receiver_phone_number")
        if not receiver_phone_number:
            return "The receiver's phone number must not be empty."
        if not re.search("^\d{9}$", receiver_phone_number):
            return "The receiver's phone number must consist of exactly " \
                "9 digits."
        image = request.files.get("image")
        if not image:
            return "The image must not be empty."
        if not image.filename:
            return "The image must not be empty."
        _, image_file_extension = os.path.splitext(image.filename)
        if image_file_extension.lower() not in [".png", ".jpg", ".jpeg"]:
            return "The image file format is unsupported (format: {}). " \
                "Only the PNG and JPG formats are supported.".format(
                    image_file_extension)
        return None

    def __registerPackageFromRequest(self, user_login, request):
        if not dbi.doesUserExist(user_login):
            abort(500,
                  "Could not register the package. The user does not exist "
                  "(user_login: {}).".format(user_login))
        sender_phone_number = request.form.get("sender_phone_number")
        receiver_phone_number = request.form.get("receiver_phone_number")
        image = request.files.get("image")
        if not image:
            abort(500,
                  "Could not register the package. The image must not be "
                  "empty.")
        if not image.filename:
            abort(500,
                  "Could not register the package. The image must not be "
                  "empty.")
        _, image_file_extension = os.path.splitext(image.filename)
        if image_file_extension.lower() not in [".png", ".jpg", ".jpeg"]:
            abort(500, "Could not register the package. The image file format "
                  "is unsupported (format: {}). Only the PNG and JPG formats "
                  "are supported.".format(image_file_extension))
        serial_number = str(uuid.uuid4()).replace("-", "")
        sender = Person(
            request.form.get("sender_name"),
            request.form.get("sender_surname"))
        sender_address = Address(
            request.form.get("sender_street"),
            request.form.get("sender_building_number"),
            request.form.get("sender_apartment_number"),
            request.form.get("sender_postal_code"),
            request.form.get("sender_city"),
            request.form.get("sender_country"))
        receiver = Person(
            request.form.get("receiver_name"),
            request.form.get("receiver_surname"))
        receiver_address = Address(
            request.form.get("receiver_street"),
            request.form.get("receiver_building_number"),
            request.form.get("receiver_apartment_number"),
            request.form.get("receiver_postal_code"),
            request.form.get("receiver_city"),
            request.form.get("receiver_country"))
        image_file_path = "{}image_{}{}".format(
            IMAGE_FILES_DIRECTORY, serial_number, image_file_extension)
        package = Package(
            dbi.getPackageIdFromSerialNumber(serial_number),
            serial_number,
            datetime.utcnow().isoformat(),
            image_file_path,
            "",
            sender,
            sender_address,
            sender_phone_number,
            receiver,
            receiver_address,
            receiver_phone_number,
            PACKAGE_STATUS_NEW)
        package_validation_error = package.validate()
        if package_validation_error:
            abort(500,
                  "Could not register the package. The package is invalid. "
                  "{}".format(package_validation_error))
        image.save(image_file_path)
        dbi.getDatabase().set(package.id, package.toData())
        dbi.getDatabase().hset(PACKAGE_ID_TO_SENDER_ID_MAP, package.id,
                               dbi.getUserIdFromLogin(user_login))
        on_package_update(package)


@api.param("serial_number", "A package serial number.", required=True)
@package_namespace.route("/<serial_number>")
class PackageResource(Resource):

    @jwt_required
    @cross_origin()
    @api.doc(responses={200: "OK",
                        403: "Forbidden, {error_message: string}",
                        404: "Not Found, {error_message: string}"})
    def get(self, serial_number):
        """ Returns a document of the package. """
        if not dbi.doesPackageExist(serial_number):
            return jsonify(error_message="The package does not exists "
                           "(serial_number: {}).".format(serial_number)), 404
        login = get_jwt_identity()
        if not self.__validateUserAccessToPackage(login, serial_number):
            return jsonify(error_message="The user does not have access to the "
                           "package (user_login: {}, package_serial_number: "
                           "{}).".format(login, serial_number)), 403
        file_path = self.__getPackageDocumentFilePath(serial_number)
        return send_file(file_path), 200

    @jwt_required
    @cross_origin()
    @api.doc(responses={200: "OK",
                        403: "Forbidden, {error_message: string}",
                        404: "Not Found, {error_message: string}"})
    def put(self, serial_number):
        """ Assigns a package to the courier. """
        if not dbi.doesPackageExist(serial_number):
            return jsonify(error_message="The package does not exists "
                           "(serial_number: {}).".format(serial_number)), 404
        package_status = dbi.getPackageStatus(serial_number)
        if package_status != PACKAGE_STATUS_NEW:
            return jsonify(error_message="The package is not new "
                           "(serial_number: {}, status: {}).".format(
                               serial_number, package_status)), 400
        login = get_jwt_identity()
        if not dbi.isUserCourier(login):
            return jsonify(error_message="The user is not a courier "
                           "(login: {}).".format(
                               serial_number, package_status)), 403
        self.__receivePackageFromSender(login, serial_number)
        return "OK", 200

    @jwt_required
    @cross_origin()
    @api.doc(responses={200: "OK",
                        403: "Forbidden, {error_message: string}",
                        404: "Not Found, {error_message: string}"})
    def delete(self, serial_number):
        """ Deletes a package. """
        if not dbi.doesPackageExist(serial_number):
            return jsonify(error_message="The package does not exists "
                           "(serial_number: {}).".format(serial_number)), 404
        package_status = dbi.getPackageStatus(serial_number)
        if package_status != PACKAGE_STATUS_NEW:
            return jsonify(error_message="The package is not new "
                           "(serial_number: {}, status: {}).".format(
                               serial_number, package_status)), 400
        login = get_jwt_identity()
        if not self.__validateUserAccessToPackage(login, serial_number,
                                                  must_not_be_courier=True):
            return jsonify(error_message="The user does not have access to the "
                           "package or the requested operation on the package "
                           "(user_login: {}, package_serial_number: "
                           "{}).".format(login, serial_number)), 403
        self.__deletePackage(serial_number)
        return "OK", 200

    def __getPackageDocumentFilePath(self, serial_number):
        if not dbi.doesPackageExist(serial_number):
            abort(500,
                  "Could not get the package document. The package does not "
                  "exist (package_serial_number: {}).".format(serial_number))
        file_path = ""
        package = dbi.getPackage(serial_number)
        if package.document_file_path:
            file_path = package.document_file_path
            if not os.path.isfile(file_path):
                file_path = ""
        if not file_path:
            file_path = package.generateDocument()
            dbi.getDatabase().set(package.id, package.toData())
        return file_path

    def __receivePackageFromSender(self, courier_login, package_serial_number):
        if not dbi.doesUserExist(courier_login):
            abort(500,
                  "Could not receive the package from the sender. The user "
                  "does not exists (user_login: {}).".format(courier_login))
        if not dbi.isUserCourier(courier_login):
            abort(500,
                  "Could not receive the package from the sender. The user "
                  "is not a courier (user_login: {}).".format(courier_login))
        if not dbi.doesPackageExist(package_serial_number):
            abort(500,
                  "Could not receive the package from the sender. The package "
                  "does not exist (package_serial_number: {}).".format(
                      package_serial_number))
        courier_id = dbi.getUserIdFromLogin(courier_login)
        package = dbi.getPackage(package_serial_number)
        package_status = package.status
        if package_status != PACKAGE_STATUS_NEW:
            abort(500,
                  "Could not receive the package from sender. The package "
                  "is not new (package_serial_number: {}, status: {}).".format(
                      package_serial_number, package_status))
        if dbi.getDatabase().hexists(PACKAGE_ID_TO_COURIER_ID_MAP, package.id):
            courier_id = dbi.getDatabase().hget(
                PACKAGE_ID_TO_COURIER_ID_MAP,
                package.id)
            abort(500,
                  "Could not receive the package from sender. The package "
                  "already has an assigned courier (courier_id: {}, "
                  "package_serial_number: {}).".format(
                      courier_id, package_serial_number))
        package.setStatus(PACKAGE_STATUS_RECEIVED_FROM_SENDER)
        dbi.getDatabase().set(package.id, package.toData())
        dbi.getDatabase().hset(
            PACKAGE_ID_TO_COURIER_ID_MAP,
            package.id, courier_id)
        on_package_update(package)

    def __deletePackage(self, serial_number):
        if not dbi.doesPackageExist(serial_number):
            abort(500,
                  "Could not delete the package. The package does not exist "
                  "(serial_number: {}).".format(serial_number))
        package_status = dbi.getPackageStatus(serial_number)
        if package_status != PACKAGE_STATUS_NEW:
            abort(500,
                  "Could not delete the package. The package must be new "
                  "(serial_number: {}, status: {}).".format(
                      serial_number, package_status))
        package = dbi.getPackage(serial_number)
        if not dbi.getDatabase().hexists(
                PACKAGE_ID_TO_SENDER_ID_MAP,
                package.id):
            abort(500,
                  "Could not delete the package. No user match the package_id: "
                  "{}.".format(package.id))
        if os.path.isfile(package.document_file_path):
            os.remove(package.document_file_path)
        if os.path.isfile(package.image_file_path):
            os.remove(package.image_file_path)
        dbi.getDatabase().hdel(PACKAGE_ID_TO_SENDER_ID_MAP, package.id)
        dbi.getDatabase().delete(package.id)

    def __validateUserAccessToPackage(self, user_login, package_serial_number,
                                      must_be_courier=False,
                                      must_not_be_courier=False):
        if not dbi.doesUserExist(user_login):
            abort(500,
                  "Could not validate user's access to the package. The user "
                  "does not exist (user_login: {}).".format(user_login))
        if not dbi.doesPackageExist(package_serial_number):
            abort(500,
                  "Could not validate user's access to the package. "
                  "The package does not exist (package_serial_number: "
                  "{}).".format(package_serial_number))
        user_id = dbi.getUserIdFromLogin(user_login)
        package_id = dbi.getPackageIdFromSerialNumber(package_serial_number)
        if dbi.isUserCourier(user_login):
            if must_not_be_courier:
                return False
            if dbi.getDatabase().hexists(
                    PACKAGE_ID_TO_COURIER_ID_MAP,
                    package_id):
                if user_id == dbi.getDatabase().hget(
                        PACKAGE_ID_TO_COURIER_ID_MAP,
                        package_id):
                    return True
        elif must_be_courier:
            return False
        if not dbi.getDatabase().hexists(
                PACKAGE_ID_TO_SENDER_ID_MAP,
                package_id):
            abort(500,
                  "Could not validate user's access to the package. "
                  "No user match the package (user_login: {}, "
                  "package_serial_number: {}).".format(user_login,
                                                       package_serial_number))
        return user_id == dbi.getDatabase().hget(
            PACKAGE_ID_TO_SENDER_ID_MAP,
            package_id)


#
# MAILBOX NAMESPACE
#


@mailbox_namespace.route("")
class MailboxListResource(Resource):

    create_mailbox_form_model = \
        api.model("Create a Mailbox Form Model", {
            "code": fields.String(
                required=True, description="A mailbox code."),
            "description": fields.String(
                required=True, description="A mailbox description.")})

    @cross_origin()
    @api.doc(responses={200: "OK"})
    def get(self):
        """ Returns a list of mailboxes. """
        mailbox_list = dbi.getMailboxList()
        return {
            "mailbox_list": mailbox_list,
            "mailbox_count": len(mailbox_list)}, 200

    @cross_origin()
    @api.expect(create_mailbox_form_model)
    @api.doc(responses={201: "Created",
                        400: "Bad Request, {error_message: string}"})
    def post(self):
        """ Creates a new mailbox. """
        request_error = self.__validateMailboxRegisterRequest(request)
        if request_error:
            return jsonify(error_message=request_error), 400
        self.__registerMailboxFromRequest(request)
        return "Created", 201

    def __validateMailboxRegisterRequest(self, request):
        code = request.form.get("code")
        if not code:
            return "The code must not be empty."
        description = request.form.get("description")
        if not description:
            return "The description must not be empty."
        return None

    def __registerMailboxFromRequest(self, request):
        code = request.form.get("code")
        description = request.form.get("description")
        mailbox_id = dbi.getMailboxIdFromCode(code)
        mailbox = Mailbox(mailbox_id, code, description)
        mailbox_validation_error = mailbox.validate()
        if mailbox_validation_error:
            abort(500,
                  "Could not register the mailbox. The mailbox is invalid. "
                  "{}".format(mailbox_validation_error))
        dbi.getDatabase().set(mailbox.id, mailbox.toData())
        dbi.getDatabase().rpush(MAILBOX_CODE_LIST, mailbox.code)


@api.param("code", "A mailbox code.", required=True)
@mailbox_namespace.route("/<code>")
class MailboxResource(Resource):

    assign_package_to_mailbox_form_model = \
        api.model("Assign Package to Mailbox Form Model", {
            "package_serial_number": fields.String(
                required=True, description="A package serial number.")})

    assign_packages_to_courier_form_model = \
        api.model("Assign Packages to Courier Form Model", {
            "mailbox_token": fields.String(
                required=True, description="A mailbox token."),
            "package_list":
                fields.List(fields.String,
                            required=True,
                            description="A list of package serial numbers.")})

    @cross_origin()
    @api.param("token", "A mailbox token.", required=True)
    @api.doc(responses={200: "OK",
                        400: "Bad Request, {error_message: string}",
                        404: "Not Found, {error_message: string}"})
    def get(self, code):
        """ Returns a list of packages in the mailbox. """
        if not dbi.doesMailboxExist(code):
            return jsonify(error_message="The mailbox does not exist "
                           "(mailbox_code: {}).".format(code)), 404
        token = request.args.get("token")
        if not token:
            return jsonify(error_message="The token must not be empty."), 400
        if not dbi.validateMailboxToken(code, token):
            return jsonify(error_message="The token is invalid."), 400
        return self.__fetchMailboxPackageList(code), 200

    @cross_origin()
    @api.expect(assign_package_to_mailbox_form_model)
    @api.doc(responses={200: "OK",
                        400: "Bad Request, {error_message: string}",
                        404: "Not Found, {error_message: string}"})
    def post(self, code):
        """ Assigns a package to the mailbox. """
        if not dbi.doesMailboxExist(code):
            return jsonify(error_message="The mailbox does not exist "
                           "(code: {}).".format(code)), 404
        package_serial_number = request.form.get("package_serial_number")
        if not package_serial_number:
            return jsonify(error_message="The package serial number must not "
                           "be empty."), 400
        if not dbi.doesPackageExist(package_serial_number):
            return jsonify(error_message="The package does not exist "
                           "(serial_number: {}).".format(
                               package_serial_number)), 400
        package_status = dbi.getPackageStatus(package_serial_number)
        if package_status != PACKAGE_STATUS_NEW:
            return jsonify(error_message="The package is not new "
                           "(serial_number: {}, status: {}).".format(
                               package_serial_number, package_status)), 400
        self.__assignPackageToMailbox(code, package_serial_number)
        return "OK", 200

    @cross_origin()
    @api.expect(assign_packages_to_courier_form_model)
    @api.doc(responses={200: "OK",
                        400: "Bad Request, {error_message: string}",
                        404: "Not Found, {error_message: string}"})
    def delete(self, code):
        """ Assigns a package list to the courier. """
        if not dbi.doesMailboxExist(code):
            return jsonify(error_message="The mailbox does not exist "
                           "(code: {}).".format(code)), 404
        token = request.form.get("mailbox_token")
        if not token:
            return jsonify(error_message="The mailbox token must not be "
                           "empty."), 400
        validation_result = dbi.validateMailboxToken(code, token)
        if not validation_result:
            return jsonify(error_message="The mailbox token is invalid."), 400
        courier_login = validation_result[0]
        package_list_raw = request.form.get("package_list")
        if not package_list_raw:
            return jsonify(error_message="The package list must not be "
                           "empty."), 400
        package_list = package_list_raw.split(",")
        package_list[:] = [package.strip("[]").strip()
                           for package in package_list]
        if not package_list:
            return jsonify(error_message="The package list must not be "
                           "empty (an example list: \"[1a,2b,3c]\")."), 400
        for package_serial_number in package_list:
            if not dbi.doesPackageExist(package_serial_number):
                return jsonify(error_message="One of the packages does not "
                               "exist (serial number: {}).".format(
                                   package_serial_number)), 400
        self.__assignPackagesToCourier(code, courier_login, package_list)
        return "OK", 200

    def __fetchMailboxPackageList(self, mailbox_code):
        package_list = []
        mailbox_id = dbi.getMailboxIdFromCode(mailbox_code)
        for package_id in dbi.getDatabase().hkeys(PACKAGE_ID_TO_MAILBOX_ID_MAP):
            if mailbox_id == dbi.getDatabase().hget(
                    PACKAGE_ID_TO_MAILBOX_ID_MAP, package_id):
                if not dbi.getDatabase().exists(package_id):
                    abort(500,
                          "Could not fetch the mailbox package list. One of "
                          "the packages does not exist (package_id: "
                          "{}).".format(package_id))
                package = Package.loadFromData(
                    dbi.getDatabase().get(package_id))
                package_register_date = dateutil.parser.parse(
                    package.register_date)
                package_register_date_text = package_register_date.strftime(
                    "%Y-%m-%d %H:%M:%S")
                package_list.append({
                    "serial_number": package.serial_number,
                    "register_date": package_register_date_text,
                    "url": PACKAGE_SERVICE_API_URL + "/package/" +
                    package.serial_number})
        return {
            "package_list": package_list,
            "package_count": len(package_list)}

    def __assignPackageToMailbox(self, mailbox_code, package_serial_number):
        if not dbi.doesMailboxExist(mailbox_code):
            abort(500,
                  "Could not assign the package to mailbox. The mailbox "
                  "does not exist (mailbox_code: {}).".format(
                      mailbox_code))
        if not dbi.doesPackageExist(package_serial_number):
            abort(500,
                  "Could not assign the package to mailbox. The package "
                  "does not exist (package_serial_number: {}).".format(
                      package_serial_number))
        package = dbi.getPackage(package_serial_number)
        package_status = package.status
        if package_status != PACKAGE_STATUS_NEW:
            abort(500,
                  "Could not assign the package to mailbox. The package "
                  "is not new (package_serial_number: {}, status: {}).".format(
                      package_serial_number, package_status))
        mailbox_id = dbi.getMailboxIdFromCode(mailbox_code)
        if dbi.getDatabase().hexists(PACKAGE_ID_TO_MAILBOX_ID_MAP, package.id):
            mailbox_id = dbi.getDatabase().hget(
                PACKAGE_ID_TO_MAILBOX_ID_MAP,
                package.id)
            abort(500,
                  "Could not assign the package to mailbox. The package "
                  "already has an assigned mailbox (mailbox_id: {}, "
                  "package_serial_number: {}).".format(
                      mailbox_id, package_serial_number))
        package.setStatus(PACKAGE_STATUS_IN_MAILBOX)
        dbi.getDatabase().set(package.id, package.toData())
        dbi.getDatabase().hset(PACKAGE_ID_TO_MAILBOX_ID_MAP, package.id,
                               mailbox_id)
        on_package_update(package)

    def __assignPackagesToCourier(self, mailbox_code, courier_login,
                                  package_list):
        if not dbi.doesMailboxExist(mailbox_code):
            abort(500,
                  "Could not assign the packages to courier. The mailbox "
                  "does not exist (mailbox_code: {}).".format(
                      mailbox_code))
        if not dbi.doesUserExist(courier_login):
            abort(500,
                  "Could not assign the packages to courier. The user "
                  "does not exists (user_login: {}).".format(courier_login))
        if not dbi.isUserCourier(courier_login):
            abort(500,
                  "Could not assign the packages to courier. The user "
                  "is not a courier (user_login: {}).".format(courier_login))
        courier_id = dbi.getUserIdFromLogin(courier_login)
        for package_serial_number in package_list:
            if not dbi.doesPackageExist(package_serial_number):
                abort(500,
                      "Could not assign the packages to courier. One of the "
                      "packages does not exist (package_serial_number: "
                      "{}).".format(package_serial_number))
            package = dbi.getPackage(package_serial_number)
            package_status = package.status
            if package_status != PACKAGE_STATUS_IN_MAILBOX:
                abort(500,
                      "Could not assign the packages to courier. One of the "
                      "packages is not in mailbox (package_serial_number: "
                      "{}, status: {}).".format(
                          package_serial_number, package_status))
            package_id = dbi.getPackageIdFromSerialNumber(
                package_serial_number)
            if dbi.getDatabase().hexists(
                    PACKAGE_ID_TO_COURIER_ID_MAP, package_id):
                courier_id = dbi.getDatabase().hget(
                    PACKAGE_ID_TO_COURIER_ID_MAP,
                    package_id)
                abort(500,
                      "Could not assign the packages to courier. One of the "
                      "packages already has an assigned courier (courier_id: "
                      "{}, package_serial_number: {}).".format(
                          courier_id, package_serial_number))
        for package_serial_number in package_list:
            package = dbi.getPackage(package_serial_number)
            package.setStatus(PACKAGE_STATUS_RECEIVED_FROM_MAILBOX)
            dbi.getDatabase().set(package.id, package.toData())
            dbi.getDatabase().hset(PACKAGE_ID_TO_COURIER_ID_MAP, package.id,
                                   courier_id)
            dbi.getDatabase().hdel(PACKAGE_ID_TO_MAILBOX_ID_MAP, package.id)
            on_package_update(package)


#
# SOCKET IO
#


@socket_io.on("connect")
def on_connect():
    emit("connect_response", {"success": True})


@socket_io.on("disconnect")
def on_disconnect():
    pass


@socket_io.on("subscribe")
def on_join(data):
    notifier_name = data[NOTIFIER_NAME_KEY]
    if notifier_name not in NOTIFIER_NAME_LIST:
        emit("join_response", {
            "success": False,
            "error_message": "Could not subscribe to the notifier. "
                             "The notifier does not exist (name: {}).".format(
                                 notifier_name)})
        return
    join_room(notifier_name)
    emit("subscribe_response", {
        "success": True,
        NOTIFIER_NAME_KEY: notifier_name})


@socket_io.on("unsubscribe")
def on_leave(data):
    notifier_name = data[NOTIFIER_NAME_KEY]
    if notifier_name not in NOTIFIER_NAME_LIST:
        emit("leave_response", {
            "success": False,
            "error_message": "Could not unsubscribe from the notifier. "
                             "The notifier does not exist (name: {}).".format(
                                 notifier_name)})
        return
    leave_room(notifier_name)
    emit("unsubscribe_response", {
        "success": True,
        NOTIFIER_NAME_KEY: notifier_name})


def on_package_update(package):
    socket_io.emit("package_update", {
        "serial_number": package.serial_number,
        "status": package.status,
        "status_text": package.getStatusText()
    }, namespace="/", room=PACKAGE_NOTIFIER)
