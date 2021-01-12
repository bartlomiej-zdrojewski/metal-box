const Mailbox = {
    API_URL: "https://localhost:8084/api",
    sendPackage: function (mailbox_code, package_serial_number) {
        const POST = "POST";
        const HTTP_STATUS = {
            OK: 200,
            BAD_REQUEST: 400,
            NOT_FOUND: 404
        };
        const formData = new FormData();
        formData.append("package_serial_number", package_serial_number);
        const url = this.API_URL + "/mailbox/" + mailbox_code;
        const params = {
            method: POST,
            body: formData,
            redirect: "follow"
        };
        return fetch(url, params)
            .then(response => {
                const status = response.status;
                if (status === HTTP_STATUS.OK) {
                    return Promise.resolve();
                } else if (status === HTTP_STATUS.BAD_REQUEST ||
                    status === HTTP_STATUS.NOT_FOUND) {
                    return response.json().then((data) => {
                        throw data.error_message;
                    });
                } else {
                    throw "An unknown response status was returned (status: " +
                    response.status + ").";
                }
            });
    },
    fetchPackageList: function (mailbox_code, mailbox_token) {
        const GET = "GET";
        const HTTP_STATUS = {
            OK: 200,
            BAD_REQUEST: 400,
            NOT_FOUND: 404
        };
        const url = this.API_URL + "/mailbox/" + mailbox_code + "?token=" +
            mailbox_token;
        const params = {
            method: GET,
            redirect: "follow"
        };
        return fetch(url, params)
            .then(response => {
                const status = response.status;
                if (status === HTTP_STATUS.OK) {
                    return response.json();
                } else if (status === HTTP_STATUS.BAD_REQUEST ||
                    status === HTTP_STATUS.NOT_FOUND) {
                    return response.json().then((data) => {
                        throw data.error_message;
                    });
                } else {
                    throw "An unknown response status was returned (status: " +
                    response.status + ").";
                }
            });
    },
    receivePackages: function (mailbox_code, mailbox_token, package_list) {
        const DELETE = "DELETE";
        const HTTP_STATUS = {
            OK: 200,
            BAD_REQUEST: 400,
            NOT_FOUND: 404
        };
        const formData = new FormData();
        console.log(mailbox_token);
        formData.append("mailbox_token", mailbox_token);
        formData.append("package_list", package_list);
        const url = this.API_URL + "/mailbox/" + mailbox_code;
        const params = {
            method: DELETE,
            body: formData,
            redirect: "follow"
        };
        return fetch(url, params)
            .then(response => {
                const status = response.status;
                if (status === HTTP_STATUS.OK) {
                    return Promise.resolve();
                } else if (status === HTTP_STATUS.BAD_REQUEST ||
                    status === HTTP_STATUS.NOT_FOUND) {
                    return response.json().then((data) => {
                        throw data.error_message;
                    });
                } else {
                    throw "An unknown response status was returned (status: " +
                    response.status + ").";
                }
            });
    }
};

const MailboxList = {
    API_URL: "https://localhost:8084/api",
    fetchMailboxList: function () {
        const GET = "GET";
        const HTTP_STATUS = {
            OK: 200
        };
        const url = this.API_URL + "/mailbox"
        const params = {
            method: GET,
            redirect: "follow"
        };
        return fetch(url, params)
            .then(response => {
                const status = response.status;
                if (status === HTTP_STATUS.OK) {
                    return response.json();
                } else {
                    throw "An unknown response status was returned (status: " +
                    response.status + ").";
                }
            });
    }
};
