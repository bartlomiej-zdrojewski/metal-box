Aplikację można uruchomić wywołując w katalogu głównym repozytorium komendę:

JWT_SECRET="WsVm1JFHjg11ePV3wzGQsxsPAJOBIUzgmScWkMLPnR0=" docker-compose up

Gdzie JWT_SECRET to klucz szyfrujący dla mechanizmu JWT, którego wartość można zastąpić
innym losowym ciągiem znaków. Po uruchomieniu, aplikacja dostępna będzie pod adresem:

https://localhost:8080

Uwaga! Aby umożliwić rejestrowanie paczek i pobieranie plików, należy najpierw wpisać
w przeglądarce adres:

https://localhost:8081/

Oraz zaakceptować niezaufane połączenie. Inaczej, podczas rejestracji paczki lub pobierania
pliku zostanie zwrócony błąd "ERR_CERT_AUTHORITY_INVALID" z powodu błędnego certyfikatu HTTPS.
