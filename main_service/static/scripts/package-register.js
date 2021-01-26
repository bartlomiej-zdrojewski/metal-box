document.addEventListener('DOMContentLoaded', function (event) {
    const FORM_ID = "form_register";
    const INPUT_SENDER_NAME_ID = "sender_name";
    const INPUT_SENDER_SURNAME_ID = "sender_surname";
    const INPUT_SENDER_STREET_ID = "sender_street";
    const INPUT_SENDER_APARTMENT_NUMBER_ID = "sender_apartment_number";
    const INPUT_SENDER_CITY_ID = "sender_city";
    const INPUT_SENDER_POSTAL_CODE_ID = "sender_postal_code";
    const INPUT_SENDER_COUNTRY_ID = "sender_country";
    const INPUT_SENDER_PHONE_NUMBER_ID = "sender_phone_number";
    const INPUT_RECEIVER_NAME_ID = "receiver_name";
    const INPUT_RECEIVER_SURNAME_ID = "receiver_surname";
    const INPUT_RECEIVER_STREET_ID = "receiver_street";
    const INPUT_RECEIVER_APARTMENT_NUMBER_ID = "receiver_apartment_number";
    const INPUT_RECEIVER_CITY_ID = "receiver_city";
    const INPUT_RECEIVER_POSTAL_CODE_ID = "receiver_postal_code";
    const INPUT_RECEIVER_COUNTRY_ID = "receiver_country";
    const INPUT_RECEIVER_PHONE_NUMBER_ID = "receiver_phone_number";
    const INPUT_IMAGE_ID = "image";
    const BUTTON_REGISTER_ID = "button_register";
    
    const POST = "POST";
    const HTTP_STATUS = {
        CREATED: 201,
        BAD_REQUEST: 400
    };
    const API_URL = "https://localhost:8084/api";

    const postalCodePattern = new RegExp(/^\d{2}-\d{3}$/);
    const phoneNumberPattern = new RegExp(/^\d{9}$/);
    const onEmptyError = "Pole nie może pozostać puste.";

    let isRegistering = false;
    let form = document.getElementById(FORM_ID);

    [
        INPUT_SENDER_NAME_ID,
        INPUT_SENDER_SURNAME_ID,
        INPUT_SENDER_STREET_ID,
        INPUT_SENDER_APARTMENT_NUMBER_ID,
        INPUT_SENDER_CITY_ID,
        INPUT_SENDER_POSTAL_CODE_ID,
        INPUT_SENDER_COUNTRY_ID,
        INPUT_SENDER_PHONE_NUMBER_ID,
        INPUT_RECEIVER_NAME_ID,
        INPUT_RECEIVER_SURNAME_ID,
        INPUT_RECEIVER_STREET_ID,
        INPUT_RECEIVER_APARTMENT_NUMBER_ID,
        INPUT_RECEIVER_CITY_ID,
        INPUT_RECEIVER_POSTAL_CODE_ID,
        INPUT_RECEIVER_COUNTRY_ID,
        INPUT_RECEIVER_PHONE_NUMBER_ID,
        INPUT_IMAGE_ID
    ].forEach(id => setInputValidation(id));
    form.addEventListener("submit", e => onSubmit(e));

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
            input.addEventListener("change", () => {
                if (!isRegistering) {
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

    // TODO add image validation
    function validateForm() {
        let isFormValid = true;
        const isSenderNameValid = validateInputNotEmpty(INPUT_SENDER_NAME_ID);
        const isSenderSurnameValid = validateInputNotEmpty(INPUT_SENDER_SURNAME_ID);
        const isSenderStreetValid = validateInputNotEmpty(INPUT_SENDER_STREET_ID);
        const isSenderApartmentNumberValid = validateInputNotEmpty(INPUT_SENDER_APARTMENT_NUMBER_ID);
        const isSenderCityValid = validateInputNotEmpty(INPUT_SENDER_CITY_ID);
        const isSenderPostalCodeValid = validatePostalCode(INPUT_SENDER_POSTAL_CODE_ID);
        const isSenderCountryValid = validateInputNotEmpty(INPUT_SENDER_COUNTRY_ID);
        const isSenderPhoneNumberValid = validatePhoneNumber(INPUT_SENDER_PHONE_NUMBER_ID);
        const isReceiverNameValid = validateInputNotEmpty(INPUT_RECEIVER_NAME_ID);
        const isReceiverSurnameValid = validateInputNotEmpty(INPUT_RECEIVER_SURNAME_ID);
        const isReceiverStreetValid = validateInputNotEmpty(INPUT_RECEIVER_STREET_ID);
        const isReceiverApartmentNumberValid = validateInputNotEmpty(INPUT_RECEIVER_APARTMENT_NUMBER_ID);
        const isReceiverCityValid = validateInputNotEmpty(INPUT_RECEIVER_CITY_ID);
        const isReceiverPostalCodeValid = validatePostalCode(INPUT_RECEIVER_POSTAL_CODE_ID);
        const isReceiverCountryValid = validateInputNotEmpty(INPUT_RECEIVER_COUNTRY_ID);
        const isReceiverPhoneNumberValid = validatePhoneNumber(INPUT_RECEIVER_PHONE_NUMBER_ID);
        const isImageVaild = validateInputNotEmpty(INPUT_IMAGE_ID);
        isFormValid &&= isSenderNameValid;
        isFormValid &&= isSenderSurnameValid;
        isFormValid &&= isSenderStreetValid;
        isFormValid &&= isSenderApartmentNumberValid;
        isFormValid &&= isSenderCityValid;
        isFormValid &&= isSenderPostalCodeValid;
        isFormValid &&= isSenderCountryValid;
        isFormValid &&= isSenderPhoneNumberValid;
        isFormValid &&= isReceiverNameValid;
        isFormValid &&= isReceiverSurnameValid;
        isFormValid &&= isReceiverStreetValid;
        isFormValid &&= isReceiverApartmentNumberValid;
        isFormValid &&= isReceiverCityValid;
        isFormValid &&= isReceiverPostalCodeValid;
        isFormValid &&= isReceiverCountryValid;
        isFormValid &&= isReceiverPhoneNumberValid;
        isFormValid &&= isImageVaild;
        setButtonRegisterEnabled(isFormValid);
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

    function validatePostalCode(id) {
        setSpan(id);
        let postalCode = getInputValue(id);
        if (postalCode == null) {
            return false;
        }
        if (postalCode.length == 0) {
            return false;
        }
        if (postalCode.match(postalCodePattern) == null) {
            setSpan(id, "Kod pocztowy musi być zgodny z formatem XX-YYY.", true);
            return false;
        }
        return true;
    }

    function validatePhoneNumber(id) {
        setSpan(id);
        let phoneNumber = getInputValue(id);
        if (phoneNumber == null) {
            return false;
        }
        if (phoneNumber.length == 0) {
            return false;
        }
        if (phoneNumber.match(phoneNumberPattern) == null) {
            setSpan(id, "Numer telefonu musi składać się dokładnie z 9 cyfr.", true);
            return false;
        }
        return true;
    }

    function getRegistrationResponseData(response) {
        let status = response.status;
        if (status === HTTP_STATUS.CREATED) {
            return Promise.resolve({
                success: true
            });
        }
        else if (status == HTTP_STATUS.BAD_REQUEST) {
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

    function register() {
        isRegistering = true;
        setButtonRegisterEnabled(false);
        setSpan(BUTTON_REGISTER_ID, "Rejestrowanie paczki...");
        let url = API_URL + "/package";
        let params = {
            method: POST,
            headers: {
                "Authorization": "Bearer " + document.cookie.replace("jwt-token=", "")
            },
            body: new FormData(form),
            redirect: "follow"
        };
        fetch(url, params)
            .then(response => getRegistrationResponseData(response))
            .then(response => {
                if (response.success) {
                    setSpan(BUTTON_REGISTER_ID, "Rejestracja paczki zakończyła się pomyślnie.");
                } else {
                    console.log("Registration error: " + response.error_message);
                    setSpan(BUTTON_REGISTER_ID, "Rejestracja paczki nie powiodła się z powodu nieprawidłowych danych formularza.", true);
                }
                isRegistering = false;
                validateForm();
            })
            .catch(error => {
                console.log(error);
                setSpan(BUTTON_REGISTER_ID, "Podczas rejestracji paczki wystąpił nieoczekiwany błąd.", true);
                isRegistering = false;
                validateForm();
            });
    }

    function onSubmit(event) {
        event.preventDefault();
        if (validateForm()) {
            register();
        }
    }
});
