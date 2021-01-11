const Mailbox = {
    API_URL: "https://localhost:8084/api"
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
