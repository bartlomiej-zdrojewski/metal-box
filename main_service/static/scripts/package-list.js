function downloadPackageDocument(event) {
    const GET = "GET";

    id = event.target.attributes["document-id"].value
    url = event.target.attributes["document-url"].value

    // TODO error handling
    // TODO sometimes sends "OPTIONS" instead of "GET" and does not download file
    fetch(url, {
        method: GET,
        headers: {
            "Authorization": "Bearer " + document.cookie.replace("jwt-token=", "")
        },
        redirect: "follow"
    })
        .then(response => response.blob())
        .then(response => {
            let objectUrl = window.URL.createObjectURL(response);
            let element = document.createElement("a");
            document.body.appendChild(element);
            element.href = objectUrl;
            element.download = "package_" + id + ".pdf";
            element.click();
            document.body.removeChild(element);
            window.URL.revokeObjectURL(objectUrl);
        });
}
