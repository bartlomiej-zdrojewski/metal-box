document.addEventListener('DOMContentLoaded', function (event) {
    const FORM_ID = "form_receive_packages";
    const INPUT_MAILBOX_CODE_ID = "mailbox_code";
    const INPUT_MAILBOX_TOKEN_ID = "mailbox_token";
    const INPUT_PACKAGE_LIST_ID = "package_list";
    const SUBMIT_BUTTON_ID = "submit_button";

    const MAILBOX_SERVICE_URL = "https://localhost:8082";

    init();

    function init() {
        const url = window.location.search;
        const urlParams = new URLSearchParams(url);
        const form = document.getElementById(FORM_ID);
        const mailboxCodeInput = document.getElementById(INPUT_MAILBOX_CODE_ID);
        const mailboxTokenInput =
            document.getElementById(INPUT_MAILBOX_TOKEN_ID);
        const packageListInput = document.getElementById(INPUT_PACKAGE_LIST_ID);
        const submitButton = document.getElementById(SUBMIT_BUTTON_ID);
        form.addEventListener("submit", e => onSubmit(e));
        submitButton.disabled = true;
        MailboxList.fetchMailboxList()
            .then(response => {
                updateMailboxCodeInput(response.mailbox_list);
                if (urlParams.get("code") != null &&
                    urlParams.get("token") != null) {
                    mailboxCodeInput.value = urlParams.get("code");
                    mailboxTokenInput.value = urlParams.get("token");
                    mailboxTokenInput.readOnly = true;
                    for (let i = 0; i < mailboxCodeInput.options.length; i++) {
                        const option = mailboxCodeInput.options[i];
                        option.disabled = true;
                    }
                    Mailbox.fetchPackageList(
                        mailboxCodeInput.value, mailboxTokenInput.value)
                        .then(response => {
                            const packageList = response.package_list;
                            for (let i = 0;
                                i < packageList.length;
                                i++) {
                                const package = packageList[i];
                                let html = "<option value=\"";
                                html += package.serial_number;
                                html += "\">";
                                html += package.serial_number;
                                html += "</option>";
                                packageListInput.innerHTML += html;
                            }
                            if (packageList.length > 0) {
                                submitButton.disabled = false;
                            }
                        })
                        .catch(error => {
                            updateStatus("Podczas pobierania listy paczek " +
                                "wystąpił błąd.", true);
                            console.log("Could not fetch the package list. " +
                                error);
                        });
                } else {
                    if (urlParams.get("code") != null) {
                        mailboxCodeInput.value = urlParams.get("code");
                    }
                    if (urlParams.get("token") != null) {
                        mailboxTokenInput.value = urlParams.get("token");
                    }
                    submitButton.innerHTML = "Pobierz listę paczek";
                    packageListInput.disabled = true;
                    submitButton.disabled = false;
                }
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
        const url = window.location.search;
        const urlParams = new URLSearchParams(url);
        const mailboxCodeInput = document.getElementById(INPUT_MAILBOX_CODE_ID);
        const mailboxTokenInput =
            document.getElementById(INPUT_MAILBOX_TOKEN_ID);
        const packageListInput = document.getElementById(INPUT_PACKAGE_LIST_ID);
        if (urlParams.get("code") != null &&
            urlParams.get("token") != null) {
            let packageList = "[";
            for (let i = 0; i < packageListInput.options.length; i++) {
                const package = packageListInput.options[i];
                if (package.selected) {
                    packageList += package.value + ",";
                }
            }
            if (packageList[packageList.length - 1] === ",") {
                packageList = packageList.substr(0, packageList.length - 1);
            }
            packageList += "]";
            if (packageList != "[]") {
                const code = mailboxCodeInput.value;
                const token = mailboxTokenInput.value;
                Mailbox.receivePackages(code, token, packageList)
                    .then(_ => {
                        updateStatus("Paczki zostały odebrane pomyślnie.")
                    }).catch(error => {
                        updateStatus("Podczas odiberania paczek wystąpił błąd.",
                            true);
                        console.log("Could not receive the packages. " + error);
                    });
            }
        } else {
            const code = mailboxCodeInput.value;
            const token = mailboxTokenInput.value;
            window.location.href = MAILBOX_SERVICE_URL + "/receive?code=" +
                code + "&token=" + token;
        }
    }
});
