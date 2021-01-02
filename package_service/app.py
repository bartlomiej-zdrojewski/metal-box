import math
import os
from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS, cross_origin
from flask_restplus import Api, Resource, fields
from db.dbi import *

app = Flask(__name__, static_url_path="")
app.config["JWT_SECRET_KEY"] = os.environ.get(JWT_SECRET_KEY)
jwt = JWTManager(app)
api = Api(app)
dbi = DatabaseInterface()

CORS(app, origins=[
    MAIN_SERVICE_ORIGIN,
    COURIER_SERVICE_ORIGIN],
    allow_headers=["Authorization"])

package_namespace = api.namespace(
    "Package",
    path="/api/package",
    description="Package Service API")


@package_namespace.route("")
class PackageListResource(Resource):

    create_package_form_model = api.model("Create Package Form Model", {
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
            required=True, description="A receiver's building number (a part of "
            "the address)."),
        "receiver_apartment_number": fields.String(
            required=True, description="A receiver's apartment number (a part of "
            "the address)."),
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
            required=True, description="A package photo. A PNG or JPEG file.")
    })

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
        if not dbi.doesUserExist(login):
            abort(500,
                  "Could not fetch the package list. The user does not exists "
                  "(login: {}).".format(login))
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
                package_is_deletable = "false"
                if package.status == PACKAGE_STATUS_NEW:
                    package_is_deletable = "true"
                package_list.append({
                    "serial_number": package.serial_number,
                    "register_date": package_register_date_text,
                    "status": package.getStatusText(),
                    "url": PACKAGE_SERVICE_API_URL + "/package/" +
                    package.serial_number,
                    "is_deletable": package_is_deletable
                })
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
                "package_count": len(package_list)
            }

    def __validatePackageRegisterRequest(self, request):
        sender = Person(
            request.form.get("sender_name"),
            request.form.get("sender_surname")
        )
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
            request.form.get("sender_country")
        )
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
                  "exist (serial_number: {}).".format(serial_number))
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
                  "does not exists (login: {}).".format(courier_login))
        if not dbi.isUserCourier(courier_login):
            abort(500,
                  "Could not receive the package from the sender. The user "
                  "is not a courier (login: {}).".format(courier_login))
        if not dbi.doesPackageExist(package_serial_number):
            abort(500,
                  "Could not receive the package from the sender. The package "
                  "does not exist (serial_number: {}).".format(
                      package_serial_number))
        courier_id = dbi.getUserIdFromLogin(courier_login)
        package_id = dbi.getPackageIdFromSerialNumber(package_serial_number)
        package = dbi.getPackage(package_serial_number)
        package_status = package.getStatus()
        if package_status != PACKAGE_STATUS_NEW:
            abort(500,
                  "Could not receive the package from sender. The package "
                  "is not new (serial_number: {}, status: {}).".format(
                      package_serial_number, package_status))
        if dbi.getDatabase().hexists(PACKAGE_ID_TO_COURIER_ID_MAP, package_id):
            courier_id = dbi.getDatabase().hget(
                PACKAGE_ID_TO_COURIER_ID_MAP,
                package_id)
            abort(500,
                  "Could not receive the package from sender. The package "
                  "already has an assigned courier (courier_id: {}, "
                  "package_serial_number: {}).".format(
                      courier_id, package_serial_number))
        package.setStatus(PACKAGE_STATUS_RECEIVED_FROM_SENDER)
        dbi.getDatabase().set(package_id, package.toData())
        dbi.getDatabase().hset(
            PACKAGE_ID_TO_COURIER_ID_MAP,
            package_id, courier_id)

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
                  "does not exist (login: {}).".format(user_login))
        if not dbi.doesPackageExist(package_serial_number):
            abort(500,
                  "Could not validate user's access to the package. "
                  "The package does not exist (serial_number: {}).".format(
                      package_serial_number))
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
