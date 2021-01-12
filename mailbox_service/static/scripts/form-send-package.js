document.addEventListener('DOMContentLoaded', function (event) {
    const FORM_ID = "form_send_package";
    const INPUT_MAILBOX_CODE_ID = "mailbox_code";
    const INPUT_PACKAGE_SERIAL_NUMBER_ID = "package_serial_number";
    const SUBMIT_BUTTON_ID = "submit_button";

    init();

    function init() {
        const form = document.getElementById(FORM_ID);
        const submitButton = document.getElementById(SUBMIT_BUTTON_ID);
        form.addEventListener("submit", e => onSubmit(e));
        submitButton.disabled = true;
        MailboxList.fetchMailboxList()
            .then(response => {
                updateMailboxCodeInput(response.mailbox_list);
                submitButton.disabled = false;
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
        const mailbox_code =
            document.getElementById(INPUT_MAILBOX_CODE_ID).value;
        const package_serial_number =
            document.getElementById(INPUT_PACKAGE_SERIAL_NUMBER_ID).value;
        Mailbox.sendPackage(mailbox_code, package_serial_number)
            .then(_ => {
                updateStatus("Paczka została nadana pomyślnie.")
            }).catch(error => {
                updateStatus("Podczas nadawania paczki wystąpił błąd. " +
                    "Upewnij się, że numer seryjny paczki jest poprawny.",
                    true);
                console.log("Could not send the package. " + error);
            });
    }
});
