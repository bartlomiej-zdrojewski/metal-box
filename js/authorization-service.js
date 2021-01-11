// TODO login, register, logout

const Authorization = {
    API_URL: "https://localhost:8083/api",
    fetchMailboxToken: function (mailbox_code) {
        const POST = "POST";
        const HTTP_STATUS = {
            OK: 200,
            BAD_REQUEST: 400,
            UNAUTHORIZED: 401,
            FORBIDDEN: 403
        };
        const formData = new FormData();
        formData.append("mailbox_code", mailbox_code);
        const url = this.API_URL + "/user/mailbox_token";
        const params = {
            method: POST,
            body: formData,
            credentials: "include",
            redirect: "follow"
        };
        return fetch(url, params)
            .then(response => {
                const status = response.status;
                if (status === HTTP_STATUS.OK) {
                    return response.json();
                } else if (status === HTTP_STATUS.BAD_REQUEST ||
                    status === HTTP_STATUS.UNAUTHORIZED ||
                    status === HTTP_STATUS.FORBIDDEN) {
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
