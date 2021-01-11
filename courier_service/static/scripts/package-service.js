const Package = {
    onDownloadDocument: function (element) {
        package_url = element.attributes["package-url"].value;
        package_serial_number =
            element.attributes["package-serial-number"].value;
        this.downloadDocument(package_url, package_serial_number);
    },
    onDelete: function (element) {
        package_url = element.attributes["package-url"].value
        this.delete(package_url);
    },
    downloadDocument: function (package_url, package_serial_number) {
        const GET = "GET";
        const HTTP_STATUS = {
            OK: 200
        };
        const params = this.__getRequestParams(GET);
        fetch(package_url, params)
            .then(response => {
                if (response.status === HTTP_STATUS.OK) {
                    return response.blob();
                }
                return response.json().then((data) => {
                    throw data.error_message;
                });
            })
            .then(response => {
                let objectUrl = window.URL.createObjectURL(response);
                let element = document.createElement("a");
                document.body.appendChild(element);
                element.href = objectUrl;
                element.download = "package_" + package_serial_number + ".pdf";
                element.click();
                document.body.removeChild(element);
                window.URL.revokeObjectURL(objectUrl);
            }).catch(error => {
                console.log("Could not download the package document. " +
                    error);
            });
    },
    delete: function (package_url) {
        const DELETE = "DELETE";
        const HTTP_STATUS = {
            OK: 200
        };
        const params = this.__getRequestParams(DELETE);
        fetch(package_url, params)
            .then(response => {
                if (response.status === HTTP_STATUS.OK) {
                    window.location.reload();
                }
                return response.json().then((data) => {
                    throw data.error_message;
                });
            }).catch(error => {
                console.log("Could not delete the package. " + error);
            });
    },
    __getRequestParams: function (method) {
        return {
            method: method,
            headers: {
                "Authorization":
                    "Bearer " +
                    document.cookie.replace("jwt-token=", "")
            },
            redirect: "follow"
        };
    }
};

const PackageList = {
    onPageChange: function (element) {
        page_url = element.attributes["page-url"].value;
        this.fetchPage(page_url)
            .then(page => this.onPageChangeCallback(element, page))
            .catch(error => {
                console.log("Could not fetch the package list. " + error);
            });
    },
    onPageChangeCallback: function (element, page) { },
    getPageUrl: function (api_url, page_index, page_size, as_courier) {
        let isFirstParameter = true;
        let pageUrl = api_url + "/package";
        if (typeof page_index !== 'undefined') {
            if (isFirstParameter) {
                pageUrl += "?page_index=" + page_index;
                isFirstParameter = false;
            } else {
                pageUrl += "&page_index=" + page_index;
            }
        }            
        if (typeof page_size !== 'undefined') {
            if (isFirstParameter) {
                pageUrl += "?page_size=" + page_size;
                isFirstParameter = false;
            } else {
                pageUrl += "&page_size=" + page_size;
            }
        }
        if (typeof as_courier !== 'undefined') {
            if (isFirstParameter) {
                pageUrl += "?as_courier=" + as_courier;
                isFirstParameter = false;
            } else {
                pageUrl += "&as_courier=" + as_courier;
            }
        }
        return pageUrl;
    },
    fetchPage: function (page_url) {
        const GET = "GET";
        const HTTP_STATUS = {
            OK: 200,
            BAD_REQUEST: 400
        };
        const params = this.__getRequestParams(GET);
        return fetch(page_url, params).then(response => {
            const status = response.status;
            if (status === HTTP_STATUS.OK) {
                return response.json();
            } else if (status == HTTP_STATUS.BAD_REQUEST) {
                return response.json().then((data) => {
                    throw data.error_message;
                });
            } else {
                throw "An unknown response status was returned (status: " +
                response.status + ").";
            }
        })
    },
    __getRequestParams: function (method) {
        return {
            method: method,
            headers: {
                "Authorization":
                    "Bearer " +
                    document.cookie.replace("jwt-token=", "")
            },
            redirect: "follow"
        };
    }
};

const PackageNotifier = {
    onPackageUpdateCallback: function (package) { },
    getSocket: function (socket_url) {
        socket = io.connect(socket_url);
        socket.on("connect_response", function (response) {
            if (response.success === true) {
                console.log("Connected to the socket: " + socket_url + ".");
            } else {
                console.log("Could not connect to the socket: " +
                    socket_url + ".");
            }
        });
        socket.on("subscribe_response", function (response) {
            if (response.success === true) {
                console.log("Subscribed to the notifier: " +
                    response.notifier_name + ".");
            } else {
                console.log(response.error_message);
            }
        });
        socket.on("unsubscribe_response", function (response) {
            if (response.success === true) {
                console.log("Unsubscribed from the notifier: " +
                    response.notifier_name + ".");
            } else {
                console.log(response.error_message);
            }
        });
        return socket;
    },
    subscribe: function (socket) {
        socket.on("package_update",
            (response) => this.onPackageUpdateCallback(response));
        socket.emit("subscribe", { notifier_name: "package_notifier" });
    },
    unsibscribe: function (socket) {
        socket.on("package_update", function (response) { });
        socket.emit("unsubscribe", { notifier_name: "package_notifier" });
    }
};
