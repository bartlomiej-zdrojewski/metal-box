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
        pageUrl = api_url + "/package";
        if (page_index)
            pageUrl += "?page_index=" + page_index;
        if (page_size)
            pageUrl += "?page_size=" + page_size;
        if (as_courier)
            pageUrl += "?as_courier=" + as_courier;
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
