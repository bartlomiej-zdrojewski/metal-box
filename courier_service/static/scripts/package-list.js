document.addEventListener('DOMContentLoaded', function (event) {
    const PACKAGE_LIST_TABLE_CLASS_NAME = "package-list-table";
    const PACKAGE_URL_ATTRIBUTE_NAME = "package-url";
    const PACKAGE_SERIAL_NUMBER_ATTRIBUTE_NAME = "package-serial-number";
    const PAGE_URL_ATTRIBUTE_NAME = "page-url";
    const API_URL = "https://localhost:8084/api";
    const SOCKET_URL = "https://localhost:8084/"
    const FETCH_AS_COURIER = true;    

    PackageList.onPageChangeCallback = function (element, page) {
        const table = getPackageListTableParent(element);
        if (table) {
            updatePackageListTable(table, page);
        }
    }

    PackageNotifier.onPackageUpdateCallback = function (package) {
        const tables = getPackageListTables();
        for (let i = 0; i < tables.length; i++) {
            const table = tables[i];
            const page = JSON.parse(table.getAttribute("page"));
            if (package.status === "package_status_received_from_mailbox" ||
                package.status === "package_status_received_from_sender") {
                const pageUrl = PackageList.getPageUrl(
                    API_URL, page.page_index, page.page_size, FETCH_AS_COURIER);
                PackageList.fetchPage(pageUrl)
                    .then(response => {
                        updatePackageListTable(table, response);
                    })
                    .catch(error => {
                        console.log("Could not fetch the package list. " +
                            error);
                    });
            } else {
                for (let j = 0; j < page.package_list.length; j++) {
                    if (page.package_list[j].serial_number ===
                        package.serial_number) {
                        page.package_list[j].status = package.status;
                        page.package_list[j].status_text = package.status_text;
                    }
                }
                updatePackageListTable(table, page);
            }
        }
    }

    init();

    function init() {
        const tables = getPackageListTables();
        const pageUrl = PackageList.getPageUrl(
            API_URL, undefined, undefined, FETCH_AS_COURIER);
        PackageList.fetchPage(pageUrl)
            .then(response => {
                for (let i = 0; i < tables.length; i++) {
                    const table = tables[i];
                    updatePackageListTable(table, response);
                }
            })
            .catch(error => {
                console.log("Could not fetch the package list. " + error);
            });
        const socket = PackageNotifier.getSocket(SOCKET_URL);
        PackageNotifier.subscribe(socket);
    }

    function getPackageListTables() {
        return document.getElementsByClassName(PACKAGE_LIST_TABLE_CLASS_NAME);
    }

    function getPackageListTableParent(element) {
        while (element.parentNode) {
            const classList = element.parentNode.className.split(" ");
            for (let i = 0; i < classList.length; i++) {
                if (classList[i] === PACKAGE_LIST_TABLE_CLASS_NAME) {
                    return element.parentNode;
                }
            }
            element = element.parentNode;
        }
        return null;
    }

    function updatePackageListTable(table, page) {
        // TODO move from attribute to memory
        table.setAttribute("page", JSON.stringify(page));
        const tbody = table.getElementsByTagName("tbody")[0];
        const tfoot = table.getElementsByTagName("tfoot")[0];
        if (tbody) {
            let html = "";
            const packageList = page.package_list;
            for (let i = 0; i < packageList.length; i++) {
                const package = packageList[i];
                html += "<tr>";
                html += "<td>" + package.serial_number + "</td>";
                html += "<td>" + package.register_date + "</td>";
                html += "<td>" + package.status_text + "</td>";
                html += "<td>";
                html += "<a href=\"#\" ";
                html += PACKAGE_URL_ATTRIBUTE_NAME;
                html += "=\"" + package.url + "\" ";
                html += PACKAGE_SERIAL_NUMBER_ATTRIBUTE_NAME;
                html += "=\"" + package.serial_number + "\" ";
                html += "onclick=\"Package.onDownloadDocument(this)\">"
                html += "Pobierz";
                html += "</a>";
                html += "</td>";
                html += "</tr>";
            }
            tbody.innerHTML = html;
        }
        if (tfoot) {
            let html = "";
            if ("first_page" in page) {
                html += "<span> </span>";
                html += "<a href=\"#\" ";
                html += PAGE_URL_ATTRIBUTE_NAME;
                html += "=\"" + page.first_page_url + "\" ";
                html += "onclick=\"PackageList.onPageChange(this)\">";
                html += "&lt;&lt;"
                html += "</a>";
                html += "<span> </span>";
            }
            if ("previous_page" in page) {
                html += "<span> </span>";
                html += "<a href=\"#\" ";
                html += PAGE_URL_ATTRIBUTE_NAME;
                html += "=\"" + page.previous_page_url + "\" ";
                html += "onclick=\"PackageList.onPageChange(this)\">";
                html += "&lt;"
                html += "</a>";
                html += "<span> </span>";
            }
            html += "Strona " + (page.page_index + 1) + " / " + page.page_count;
            if ("next_page_url" in page) {
                html += "<span> </span>";
                html += "<a href=\"#\" ";
                html += PAGE_URL_ATTRIBUTE_NAME;
                html += "=\"" + page.next_page_url + "\" ";
                html += "onclick=\"PackageList.onPageChange(this)\">";
                html += "&gt;"
                html += "</a>";
            }
            if ("last_page" in page) {
                html += "<span> </span>";
                html += "<a href=\"#\" ";
                html += PAGE_URL_ATTRIBUTE_NAME;
                html += "=\"" + page.last_page_url + "\" ";
                html += "onclick=\"PackageList.onPageChange(this)\">";
                html += "&gt;&gt;"
                html += "</a>";
            }
            html += "<br />";
            html += "Łącznie " + page.package_count + " paczek.";
            tfoot.innerHTML = html;
        }
    }
});
