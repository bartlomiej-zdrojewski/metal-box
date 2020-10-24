document.addEventListener('DOMContentLoaded', function (event) {
    const FORM_ID = "form-registration";
    const INPUT_LOGIN_ID = "login";
    const INPUT_PESEL_ID = "pesel";
    const INPUT_PASSWORD_ID = "password";
    const INPUT_PASSWORD_REPEAT_ID = "second_password";
    const BUTTON_REGISTER_ID = "button-register";

    const GET = "GET";
    const POST = "POST";
    const HTTP_STATUS = {
        OK: 200,
        CREATED: 201,
        NOT_FOUND: 404
    };
    const API_URL = "https://pamiw2020registration.herokuapp.com/";

    const loginPattern = new RegExp("^[a-zA-Z]+$");
    const passwordPattern = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%&*])(.*)$");
    const peselPattern = new RegExp("^[0-9]+$");

    let form = document.getElementById(FORM_ID);
    let isLoginValid = false;
    let isRegistering = false;

    form.addEventListener("submit", e => onSubmit(e));

    [
        INPUT_LOGIN_ID,
        INPUT_PESEL_ID,
        INPUT_PASSWORD_ID,
        INPUT_PASSWORD_REPEAT_ID
    ].forEach(id => setInputValidation(id));

    validateForm();
    setSpan(BUTTON_REGISTER_ID, "Wszystkie pola muszą zostać poprawnie wypełnione.");

    function getParagraph(id) {
        let paragraps = form.getElementsByTagName("p");
        for (let i = 0; i < paragraps.length; i++) {
            let input = paragraps[i].getElementsByTagName("input")[0];
            if (input == null) {
                continue;
            }
            if (input.id === id) {
                return paragraps[i];
            }
        }
        return null;
    }

    function getInputValue(id) {
        let paragraph = getParagraph(id);
        if (paragraph != null) {
            let input = paragraph.getElementsByTagName("input")[0];
            if (input != null) {
                return input.value;
            }
        }
        return null;
    }

    function setInputValue(id, value) {
        let paragraph = getParagraph(id);
        if (paragraph != null) {
            let input = paragraph.getElementsByTagName("input")[0];
            if (input != null) {
                input.value = value;
                return true;
            }
        }
        return false;
    }

    function setInputValidation(id) {
        input = document.getElementById(id);
        if (input != null) {
            if (id === INPUT_LOGIN_ID) {
                input.addEventListener("change", () => {
                    if (!isRegistering) {
                        onLoginChanged();
                    }
                });
            } else {
                input.addEventListener("change", () => {
                    if (!isRegistering) {
                        validateForm();
                    }
                });
            }
            return true;
        }
        return false;
    }

    function setSpan(id, text, isError) {
        let paragraph = getParagraph(id);
        if (paragraph == null) {
            return false;
        }
        let inputValue = getInputValue(id);
        let spans = paragraph.getElementsByTagName("span");
        for (let i = 0; i < spans.length; i++) {
            paragraph.removeChild(spans[i]);
        }
        if (text !== undefined) {
            let spanHtml = "<span";
            if (id === BUTTON_REGISTER_ID || isError === true) {
                spanHtml += " class=\"";
                if (id === BUTTON_REGISTER_ID) {
                    spanHtml += "status ";
                }
                if (isError === true) {
                    spanHtml += "error "
                }
                spanHtml = spanHtml.substring(0, spanHtml.length - 1);
                spanHtml += "\"";
            }
            spanHtml += ">";
            spanHtml += text;
            spanHtml += "</span>";
            paragraph.innerHTML += spanHtml;
        }
        setInputValue(id, inputValue);
        setInputValidation(id);
        return true;
    }

    function setButtonRegisterEnabled(isEnabled) {
        let button = document.getElementById(BUTTON_REGISTER_ID);
        if (button == null || typeof (isEnabled) != "boolean") {
            return false;
        }
        button.disabled = !isEnabled;
        return true;
    }

    function validateForm() {
        let isFormValid = true;
        let isPeselValid = validatePesel();
        let isPasswordValid = validatePassword();
        let isPasswordRepeatValid = validatePasswordRepeat();
        isFormValid &&= isLoginValid;
        isFormValid &&= isPeselValid;
        isFormValid &&= isPasswordValid;
        isFormValid &&= isPasswordRepeatValid;
        setButtonRegisterEnabled(isFormValid);
        return isFormValid;
    }

    function validateLogin() {
        let login = getInputValue(INPUT_LOGIN_ID);
        if (login == null) {
            return false;
        }
        if (login.length == 0) {
            return false;
        }
        if (login.length < 5) {
            setSpan(INPUT_LOGIN_ID, "Login musi składać się z co najmniej 5 znaków.", true)
            return false;
        }
        if (login.match(loginPattern) == null) {
            setSpan(INPUT_LOGIN_ID, "Login musi składać się wyłącznie z małych i wielkich liter alfabetu łacińskiego.", true)
            return false;
        }
        return true;
    }

    // See https://www.gov.pl/web/gov/czym-jest-numer-pesel
    function validatePesel() {
        setSpan(INPUT_PESEL_ID);
        let pesel = getInputValue(INPUT_PESEL_ID);
        if (pesel == null) {
            return false;
        }
        if (pesel.length == 0) {
            return false;
        }
        if (pesel.length != 11) {
            setSpan(INPUT_PESEL_ID, "PESEL musi składać się z dokładnie 11 znaków.", true)
            return false;
        }
        if (pesel.match(peselPattern) == null) {
            setSpan(INPUT_PESEL_ID, "PESEL musi składać się wyłącznie z cyfr.", true)
            return false;
        }
        let checksum = 0;
        for (let i = 0; i < (pesel.length - 1); i++) {
            let digit = (pesel[i] * ([1, 3, 7, 9])[i % 4]) % 10;
            checksum += digit;
        }
        checksum = (10 - (checksum % 10)) % 10;
        if (pesel[10] != checksum) {
            setSpan(INPUT_PESEL_ID, "PESEL jest nieprawidłowy. Cyfra kontrolna ma nieprawidłową wartość (" + pesel[10] + " vs " + checksum + ").", true)
            return false;
        }
        return true;
    }

    function validatePassword() {
        setSpan(INPUT_PASSWORD_ID);
        let password = getInputValue(INPUT_PASSWORD_ID);
        if (password == null) {
            return false;
        }
        if (password.length == 0) {
            return false;
        }
        if (password.length < 8) {
            setSpan(INPUT_PASSWORD_ID, "Hasło musi składać się z co najmniej 8 znaków.", true)
            return false;
        }
        if (password.match(passwordPattern) == null) {
            setSpan(INPUT_PASSWORD_ID, "Hasło musi zawierać małą i wielką literę, cyfrę i znak specjalny (!@#$%&*).", true)
            return false;
        }
        return true;
    }

    function validatePasswordRepeat() {
        setSpan(INPUT_PASSWORD_REPEAT_ID);
        let password = getInputValue(INPUT_PASSWORD_ID);
        let passwordRepeat = getInputValue(INPUT_PASSWORD_REPEAT_ID);
        if (password == null || passwordRepeat == null) {
            return false;
        }
        if (passwordRepeat.length == 0) {
            return false;
        }
        if (password != passwordRepeat) {
            setSpan(INPUT_PASSWORD_REPEAT_ID, "Powtórzenie hasła nie pasuje do oryginalnego hasła.", true)
            return false;
        }
        return true;
    }

    function checkLoginAvailability() {
        let login = getInputValue(INPUT_LOGIN_ID);
        let url = API_URL + "user/" + login;

        return Promise.resolve(fetch(url, { method: GET }).then(response => {
            return response.status;
        }).catch(function (error) {
            return error.status;
        }));
    }

    function isLoginAvailable() {
        return Promise.resolve(checkLoginAvailability().then(statusCode => {
            if (statusCode === HTTP_STATUS.OK) {
                return false;

            } else if (statusCode === HTTP_STATUS.NOT_FOUND) {
                return true

            } else {
                throw "Unexpected login availability status: " + statusCode;
            }
        }));
    }

    function getRegistrationResponseData(response) {
        let status = response.status;
        if (status === HTTP_STATUS.OK || status === HTTP_STATUS.CREATED) {
            return response.json();
        } else {
            throw "Unexpected registration response status: " + response.status;
        }
    }

    function register() {
        isRegistering = true;
        setButtonRegisterEnabled(false);
        setSpan(BUTTON_REGISTER_ID, "Rejestrowanie...");
        let url = API_URL + "register";
        let params = {
            method: POST,
            body: new FormData(form),
            redirect: "follow"
        };
        fetch(url, params)
            .then(response => getRegistrationResponseData(response))
            .then(response => {
                let status = response.registration_status;
                if (status !== "OK") {
                    console.log("Registration errors: " + response.errors);
                    setSpan(BUTTON_REGISTER_ID, "Rejestracja nie powiodła się z powodu nieprawidłowych danych formularza.", true);
                } else {
                    setSpan(BUTTON_REGISTER_ID, "Rejestracja zakończyła się pomyślnie.");
                }
                isRegistering = false;
                onLoginChanged();
            })
            .catch(error => {
                console.log(error);
                setSpan(BUTTON_REGISTER_ID, "Podczas rejestracji wystąpił nieoczekiwany błąd.", true);
                isRegistering = false;
                validateForm();
            });
    }

    function onLoginChanged() {
        isLoginValid = false;
        setSpan(INPUT_LOGIN_ID);
        if (validateLogin() == false) {
            return false;
        }
        setSpan(INPUT_LOGIN_ID, "Sprawdzanie dostępności loginu...");
        isLoginAvailable().then(isAvailable => {
            if (isAvailable) {
                isLoginValid = true;
                setSpan(INPUT_LOGIN_ID, "Login jest dostępny.");
            } else {
                setSpan(INPUT_LOGIN_ID, "Login jest niedostępny.", true);
            }
            validateForm();
        }).catch(error => {
            console.log(error);
            setSpan(INPUT_LOGIN_ID, "Podczas sprawdzania dostępności loginu wystąpił nieoczekiwany błąd.", true);
            validateForm();
        });
        return true;
    }

    function onSubmit(event) {
        event.preventDefault();
        if (validateForm()) {
            register();
        }
    }
});
