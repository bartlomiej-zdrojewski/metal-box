document.addEventListener('DOMContentLoaded', function (event) {
    const GET = "GET";
    const POST = "POST";
    const HTTP_STATUS = { OK: 200, NOT_FOUND: 404 };

    let loginInput = document.getElementById("login");
    let registrationForm = document.getElementById("registration-form");

    loginInput.addEventListener("change", onLoginChanged);
    registrationForm.addEventListener("submit", (e) => onSubmit(e));

    function onLoginChanged() {
        isLoginAvailable().then(function (isAvailable) {
            let loginAvailabilitySpan = document.getElementById("login-availability");
            if (isAvailable) {
                loginAvailabilitySpan.innerHTML = "Login jest dostępny.";
            } else {
                loginAvailabilitySpan.innerHTML = "Login nie jest dostępny.";
            }
        }).catch(function (error) {
            console.error("Something went wrong while checking login availability.");
            console.error(error);
        });
    }

    function onSubmit(event) {
        event.preventDefault();
        isLoginAvailable().then(function (isAvailable) {
            if (isAvailable) {
                register();
            }
        }).catch(function (error) {
            console.error("Something went wrong while checking login availability.");
            console.error(error);
        });
    }

    function checkLoginAvailability() {
        let loginInput = document.getElementById("login");
        let baseUrl = "https://pamiw2020registration.herokuapp.com/user/";
        let userUrl = baseUrl + loginInput.value;

        return Promise.resolve(fetch(userUrl, { method: GET }).then(function (response) {
            return response.status;
        }).catch(function (error) {
            return error.status;
        }));
    }

    function isLoginAvailable() {
        return Promise.resolve(checkLoginAvailability().then(function (statusCode) {
            if (statusCode === HTTP_STATUS.OK) {
                return false;
            } else if (statusCode === HTTP_STATUS.NOT_FOUND) {
                return true
            } else {
                throw "Unknown login availability status: " + statusCode;
            }
        }));
    }

    function getRegisterRequestBody() {
        let formData = new FormData();
        let fields = ["pesel", "login", "password", "second_password"];
        fields.forEach(function (field) {
            formData.append(field, document.getElementById(field).value);
        });
        return formData;
    }

    function register() {
        let url = "https://pamiw2020registration.herokuapp.com/register";
        fetch(url, {
            method: POST,
            body: getRegisterRequestBody()
        }).then(function (response) {
            response.json().then(function (data) {
                console.log(data);
            });
        });
    }
});
