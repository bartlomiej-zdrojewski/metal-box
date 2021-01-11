document.addEventListener('DOMContentLoaded', function (event) {
    const FORM_ID = "form_generate_mailbox_token";
    const INPUT_MAILBOX_CODE_ID = "mailbox_code"
    const SUBMIT_BUTTON_ID = "submit_button";

    const MAILBOX_SERVICE_URL = "https://localhost:8082";

    init();

    function init() {
        const form = document.getElementById(FORM_ID);
        const submit_button = document.getElementById(SUBMIT_BUTTON_ID);
        form.addEventListener("submit", e => onSubmit(e));
        submit_button.disabled = true;
        MailboxList.fetchMailboxList()
            .then(response => {
                updateMailboxCodeInput(response.mailbox_list)
                submit_button.disabled = false;
            }).catch(error => {
                console.log("Could not fetch the mailbox list. " + error);
            });
    }

    function updateMailboxCodeInput(mailbox_list) {
        const mailboxCodeInput = document.getElementById(INPUT_MAILBOX_CODE_ID);
        if (mailboxCodeInput) {
            html = "";
            for (let i = 0; i < mailbox_list.length; i++) {
                const mailbox = mailbox_list[i];
                html += "<option value=\"" + mailbox.code + "\">";
                html += "(" + mailbox.code + ") " + mailbox.description;
                html += "</option>";
            }
            mailboxCodeInput.innerHTML = html;
        }
    }

    function updateStatus(text, isError) {
        const form = document.getElementById(FORM_ID);
        let status = form.getElementsByClassName("alert")[0];
        if (!status) {
            form.innerHTML += "<div class=\"mt-3 alert\"></div>";
            status = form.getElementsByClassName("alert")[0];
        }
        status.innerHTML = text;
        if (isError === true) {
            status.classList.remove('alert-primary');
            status.classList.add('alert-danger');
        } else {
            status.classList.add('alert-primary');
            status.classList.remove('alert-danger');
        }
    }

    function onSubmit(event) {
        event.preventDefault();
        mailbox_code = document.getElementById(INPUT_MAILBOX_CODE_ID).value;
        Authorization.fetchMailboxToken(mailbox_code)
            .then(response => {
                text = "Wygenerowano żeton paczkomatu: ";
                text += "<a href=\"" + MAILBOX_SERVICE_URL + "/receive?token=";
                text += response.mailbox_token;
                text += "\">";
                text += response.mailbox_token;
                text += "</a>";
                updateStatus(text)
            }).catch(error => {
                updateStatus("Podczas generowania żetonu paczkomatu " +
                    "wystąpił błąd.", true)
                console.log("Could not fetch the mailbox token. " + error);
            });
    }
});
