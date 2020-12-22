// TODO refactor

document.addEventListener('DOMContentLoaded', function (event) {
    const FORM_ID = "form_login";
    const INPUT_LOGIN_ID = "login";
    const INPUT_PASSWORD_ID = "password";
    const BUTTON_LOGIN_ID = "button_login";

    const POST = "POST";
    const HTTP_STATUS = {
        OK: 200,
        UNAUTHORIZED: 401
    };
    const API_URL = "https://localhost:8083/api";

    let isLogging = false;
    let form = document.getElementById(FORM_ID);

    [
        INPUT_LOGIN_ID,
        INPUT_PASSWORD_ID
    ].forEach(id => setInputValidation(id));
    form.addEventListener("submit", e => onSubmit(e));

    validateForm();
    setSpan(BUTTON_LOGIN_ID, "Wszystkie pola muszą zostać wypełnione.");

    function getParagraph(id) {
        let paragraps = form.getElementsByClassName("form-group");
        for (let i = 0; i < paragraps.length; i++) {
            let input = paragraps[i].getElementsByTagName("input")[0];
            if (input == null) {
                input = paragraps[i].getElementsByTagName("button")[0];
                if (input == null) {
                    continue;
                }
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
            input.addEventListener("change", () => {
                if (!isLogging) {
                    validateForm();
                }
            });
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
        let spans = paragraph.getElementsByClassName("alert");
        for (let i = 0; i < spans.length; i++) {
            paragraph.removeChild(spans[i]);
        }
        if (text !== undefined) {
            let spanHtml = "<div";
            spanHtml += " class=\"alert ";
            if (isError === true) {
                spanHtml += "alert-warning "
            } else {
                spanHtml += "alert-primary "
            }
            spanHtml += "mt-3 "
            spanHtml = spanHtml.substring(0, spanHtml.length - 1);
            spanHtml += "\"";
            spanHtml += ">";
            spanHtml += text;
            spanHtml += "</div>";
            paragraph.innerHTML += spanHtml;
        }
        setInputValue(id, inputValue);
        setInputValidation(id);
        return true;
    }

    function setButtonLoginEnabled(isEnabled) {
        let button = document.getElementById(BUTTON_LOGIN_ID);
        if (button == null || typeof (isEnabled) != "boolean") {
            return false;
        }
        button.disabled = !isEnabled;
        return true;
    }

    function validateForm() {
        let isFormValid = true;
        const isLoginValid = validateInputNotEmpty(INPUT_LOGIN_ID);
        const isPasswordValid = validateInputNotEmpty(INPUT_PASSWORD_ID);
        isFormValid &&= isLoginValid;
        isFormValid &&= isPasswordValid;
        setButtonLoginEnabled(isFormValid);
        return isFormValid;
    }

    function validateInputNotEmpty(id) {
        let inputValue = getInputValue(id);
        if (inputValue == null) {
            return false;
        }
        if (inputValue.length == 0) {
            return false;
        }
        return true;
    }

    function getLoginResponseData(response) {
        let status = response.status;
        if (status === HTTP_STATUS.OK) {
            return response.json().then((data) => {
                return {
                    success: true,
                    redirect_url: data.redirect_url
                }
            });
        }
        else if (status == HTTP_STATUS.UNAUTHORIZED) {
            return response.json().then((data) => {
                return {
                    success: false,
                    error_message: data.error_message
                }
            });
        } else {
            throw "Unexpected registration response status: " + response.status;
        }
    }

    function login() {
        isLogging = true;
        setButtonLoginEnabled(false);
        setSpan(BUTTON_LOGIN_ID, "Logowanie...");
        let url = API_URL + "/login";
        // TODO refactor
        fd = new FormData()
        fd.append("login", getInputValue("login"));
        fd.append("password", getInputValue("password"));
        fd.append("is_courier", "true");
        let params = {
            method: POST,
            body: fd,
            credentials: "include",
            redirect: "follow"
        };
        fetch(url, params)
            .then(response => getLoginResponseData(response))
            .then(response => {
                if (response.success) {
                    setSpan(BUTTON_LOGIN_ID, "Logowanie zakończyło się pomyślnie. Przekierowywanie...");
                    window.location.replace(response.redirect_url);
                } else {
                    console.log("Login error: " + response.error_message);
                    setSpan(BUTTON_LOGIN_ID, "Logowanie nie powiodło się. Nieprawidłowy login lub hasło.", true);
                    isLogging = false;
                }
            })
            .catch(error => {
                console.log(error);
                setSpan(BUTTON_LOGIN_ID, "Podczas logowania wystąpił nieoczekiwany błąd.", true);
                isLogging = false;
                validateForm();
            });
    }

    function onSubmit(event) {
        event.preventDefault();
        if (validateForm()) {
            login();
        }
    }
});
