document.addEventListener('DOMContentLoaded', function (event) {
    const STATUS_ID = "status";

    const GET = "GET";
    const HTTP_STATUS = {
        OK: 200,
        BAD_REQUEST: 400
    };
    const API_URL = "/api";

    logout();

    function setStatus(text, isError) {
        let paragraph = document.getElementById(STATUS_ID);
        if (paragraph == null) {
            return false;
        }
        paragraphHtml = "<span";
        if (isError) {
            paragraphHtml += " class=\"error\"";
        }
        paragraphHtml += ">";
        paragraphHtml += text;
        paragraphHtml += "</span>";
        paragraph.innerHTML = paragraphHtml;
        return true;
    }

    function getLogoutResponseData(response) {
        let status = response.status;
        if (status === HTTP_STATUS.OK) {
            return response.json().then((data) => {
                return {
                    success: true,
                    redirect_url: data.redirect_url
                }
            });
        }
        else if (status == HTTP_STATUS.BAD_REQUEST) {
            return response.json().then((data) => {
                return {
                    success: false,
                    error_message: data.error_message
                }
            });
        } else {
            throw "Unexpected registration response status: " + response.status;
        }
    }

    function logout() {
        let url = API_URL + "/logout";
        let params = {
            method: GET,
            redirect: "follow"
        };
        fetch(url, params)
            .then(response => getLogoutResponseData(response))
            .then(response => {
                if (response.success) {
                    setStatus("Wylogowanie zakończyło się pomyślnie. Przekierowywanie...");
                    window.location.replace(response.redirect_url);
                } else {
                    console.log("Logout error: " + response.error_message);
                    setStatus("Wylogowanie nie powiodło się. Kliknij <a href=\"/\">tutaj</a>, aby przejść na stronę główną.", true);
                }
            })
            .catch(error => {
                console.log(error);
                setStatus("Podczas wylogowywania wystąpił nieoczekiwany błąd. Kliknij <a href=\"/\">tutaj</a>, aby przejść na stronę główną.", true);
                validateForm();
            });
    }
});
