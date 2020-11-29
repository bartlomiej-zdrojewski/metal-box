function downloadPackageDocument(event) {
    id = event.target.attributes["document-id"].value
    url = event.target.attributes["document-url"].value

    fetch(url, {
        headers: {
            "Authorization": "Bearer " + document.cookie.replace("jwt-token=", ""),
            "Content-Type": "application/pdf"
        }
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
