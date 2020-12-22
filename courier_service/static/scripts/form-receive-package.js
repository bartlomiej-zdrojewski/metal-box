// TODO refactor

document.addEventListener('DOMContentLoaded', function (event) {
    const FORM_ID = "form_receive_package";
    const INPUT_SERIAL_NUMBER_ID = "serial_number";
    const BUTTON_RECEIVE_PACKAGE_ID = "button_receive_package";

    const PUT = "PUT";
    const HTTP_STATUS = {
        OK: 200,
        BAD_REQUEST: 400,
        FORBIDDEN: 403,
        NOT_FOUND: 404
    };
    const API_URL = "https://localhost:8084/api";

    isReceivingPackage = false;
    let form = document.getElementById(FORM_ID);

    [
        INPUT_SERIAL_NUMBER_ID
    ].forEach(id => setInputValidation(id));
    form.addEventListener("submit", e => onSubmit(e));

    validateForm();
    setSpan(BUTTON_RECEIVE_PACKAGE_ID, "Wszystkie pola muszą zostać wypełnione.");

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
                if (!isReceivingPackage) {
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

    function setButtonReceivePackageEnabled(isEnabled) {
        let button = document.getElementById(BUTTON_RECEIVE_PACKAGE_ID);
        if (button == null || typeof (isEnabled) != "boolean") {
            return false;
        }
        button.disabled = !isEnabled;
        return true;
    }

    function validateForm() {
        let isFormValid = true;
        const isSerialNumberValid = validateInputNotEmpty(INPUT_SERIAL_NUMBER_ID);
        isFormValid &&= isSerialNumberValid;
        setButtonReceivePackageEnabled(isFormValid);
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

    function getReceivePackageResponseData(response) {
        let status = response.status;
        if (status === HTTP_STATUS.OK) {
            return Promise.resolve({
                success: true
            });
        }
        else if (status === HTTP_STATUS.BAD_REQUEST || status === HTTP_STATUS.FORBIDDEN || status === HTTP_STATUS.NOT_FOUND) {
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

    function receivePackage() {
        isReceivingPackage = true;
        setButtonReceivePackageEnabled(false);
        setSpan(BUTTON_RECEIVE_PACKAGE_ID, "Odbieranie paczki...");
        let url = API_URL + "/package/" + getInputValue(INPUT_SERIAL_NUMBER_ID) + "/receive";
        let params = {
            method: PUT,
            headers: {
                "Authorization":
                    "Bearer " +
                    document.cookie.replace("jwt-token=", "")
            },
            redirect: "follow"
        };
        fetch(url, params)
            .then(response => getReceivePackageResponseData(response))
            .then(response => {
                if (response.success) {
                    setSpan(BUTTON_RECEIVE_PACKAGE_ID, "Paczka została odebrana pomyślnie.");
                    isReceivingPackage = false;
                } else {
                    console.log("Package receive error: " + response.error_message);
                    setSpan(BUTTON_RECEIVE_PACKAGE_ID, "Odbieranie paczki nie powiodło się. Paczka nie istnieje lub została już odebrana.", true);
                    isReceivingPackage = false;
                }
            })
            .catch(error => {
                console.log(error);
                setSpan(BUTTON_RECEIVE_PACKAGE_ID, "Podczas odbierania paczki wystąpił nieoczekiwany błąd.", true);
                isReceivingPackage = false;
                validateForm();
            });
    }

    function onSubmit(event) {
        event.preventDefault();
        if (validateForm()) {
            receivePackage();
        }
    }
});
