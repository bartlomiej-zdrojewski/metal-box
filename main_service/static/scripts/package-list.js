const GET = "GET";
const DELETE = "DELETE";
const HTTP_STATUS = {
    OK: 200
};

function downloadPackageDocument(element) {
    url = element.attributes["package-url"].value
    serial_number = element.attributes["package-serial-number"].value

    fetch(url, {
        method: GET,
        headers: {
            "Authorization":
                "Bearer " +
                document.cookie.replace("jwt-token=", "")
        },
        redirect: "follow"
    })
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
            element.download = "package_" + serial_number + ".pdf";
            element.click();
            document.body.removeChild(element);
            window.URL.revokeObjectURL(objectUrl);
        }).catch(error => {
            console.log(error);
        });
}

function deletePackage(element) {
    url = element.attributes["package-url"].value

    fetch(url, {
        method: DELETE,
        headers: {
            "Authorization":
                "Bearer " +
                document.cookie.replace("jwt-token=", "")
        },
        redirect: "follow"
    })
        .then(response => {
            if (response.status === HTTP_STATUS.OK) {
                window.location.reload();
                return Promise.resolve();
            }
            return response.json().then((data) => {
                throw data.error_message;
            });
        }).catch(error => {
            console.log(error);
        });
}
