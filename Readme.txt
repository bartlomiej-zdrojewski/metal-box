Aplikację można uruchomić wywołując w katalogu głównym repozytorium komendę:

JWT_SECRET="WsVm1JFHjg11ePV3wzGQsxsPAJOBIUzgmScWkMLPnR0=" docker-compose up

Gdzie JWT_SECRET to klucz szyfrujący dla mechanizmu JWT, którego wartość można zastąpić
innym losowym ciągiem znaków. Po uruchomieniu, aplikacja będzie dostępna pod adresem:

https://localhost:8080

Uwaga! Aby umożliwić pobieranie plików, należy najpierw otworzyć w przeglądarce adres:

https://localhost:8081/

Oraz zaakceptować niezaufane połączenie. Inaczej podczas pobierania plików zostanie
zwrócony błąd "ERR_CERT_AUTHORITY_INVALID" z powodu błędnego certyfikatu HTTPS.
