document.addEventListener('DOMContentLoaded', function (event) {
    const FORM_ID = "form-registration";
    const INPUT_LOGIN_ID = "login";
    const INPUT_PESEL_ID = "pesel";
    const INPUT_PASSWORD_ID = "password";
    const INPUT_PASSWORD_REPEAT_ID = "password-repeat";
    const BUTTON_REGISTER_ID = "button-register";

    let form = document.getElementById(FORM_ID);
    let loginInput = document.getElementById(INPUT_LOGIN_ID);
    let isLoginAvailable = false;

    form.addEventListener("submit", (e) => onSubmit(e));
    loginInput.addEventListener("change", onLoginChanged);

    [INPUT_LOGIN_ID, INPUT_PESEL_ID, INPUT_PASSWORD_ID, INPUT_PASSWORD_REPEAT_ID].forEach((id) => setInputValidation(id));

    validateForm();

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
                input.addEventListener("change", onLoginChanged);
            } else {
                input.addEventListener("change", validateForm);
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
        let isLoginValid = validateLogin();
        let isPeselValid = validatePesel();
        let isPasswordValid = validatePassword();
        let isPasswordRepeatValid = validatePasswordRepeat();
        isFormValid &&= isLoginAvailable;
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
        if (login.length < 6) {
            setSpan(INPUT_LOGIN_ID, "Login musi składać się co najmniej z 6 znaków.", true)
            return false;
        }
        // TODO ...
        return true;
    }

    function validatePesel() {
        setSpan(INPUT_PESEL_ID);
        let pesel = getInputValue(INPUT_PESEL_ID);
        if (pesel == null) {
            return false;
        }
        if (pesel.length == 0) {
            return false;
        }
        if (pesel.length < 11) {
            setSpan(INPUT_PESEL_ID, "PESEL jest za krótki.", true)
            return false;
        }
        // TODO ...
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
            setSpan(INPUT_PASSWORD_ID, "Hasło musi składać się z co najmniej 8 liter.", true)
            return false;
        }
        // TODO ...
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

    function onLoginChanged() {
        setSpan(INPUT_LOGIN_ID);
        if (validateLogin() == false) {
            return false;
        }
        setSpan(INPUT_LOGIN_ID, "Sprawdzanie dostępności loginu...")
        // TODO check login availability
        // TODO set isLoginAvailable
    }
});
