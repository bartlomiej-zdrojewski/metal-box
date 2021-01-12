Aplikację można uruchomić wywołując w katalogu głównym repozytorium komendę:

JWT_SECRET="WsVm1JFHjg11ePV3wzGQsxsPAJOBIUzgmScWkMLPnR0=" docker-compose up

Gdzie JWT_SECRET to klucz szyfrujący dla mechanizmu JWT, którego wartość można
zastąpić innym losowym ciągiem znaków.

Po uruchomieniu, interfejsy graficzne aplikacji dostępne będą pod adresami:

Interfejs główny:
    https://localhost:8080
Interfejs kuriera:
    https://localhost:8081
Interfejs paczkomatu:
    https://localhost:8082

Uwaga! Aby umożliwić poprawne funkcjonowanie aplikacji, należy najpierw wpisać
w przeglądarce adresy:

https://localhost:8083/
https://localhost:8084/

Oraz zaakceptować niezaufane połączenie. Inaczej, podczas wykonywania
zapytań do interfejsów programowania aplikacji (API) zostanie zwrócony
błąd "ERR_CERT_AUTHORITY_INVALID" z powodu błędnego certyfikatu HTTPS.

W trakcie pracy nad trzecim kamieniem milowym autoryzacja została przeniesiona
do osobnego serwisu, gdyż korzysta z niej zarówno interfejs główny, jak
i interfejs kuriera.

Punkty trzeciego kamienia milowego, które nie zostały (jeszcze) zrealizowane:
7a. Aplikacja dla kuriera ma być aplikacją progresywną z możliwością instalacji na urządzeniu mobilnym.

Punkty czwartego kamienia milowego, które nie zostały (jeszcze) zrealizowane:
1. Należy umożliwić kurierom i nadawcom logowanie do systemu z wykorzystaniem zewnętrznej autoryzacji – dowolnie wybranego systemu implementującego OAuth 2.0 (np. auth0.com). Proszę pamiętać, że jeżeli w formularzach nadawania przesyłki wykorzystują Państwo jakieś dane, które były podawane podczas rejestracji konta w klasyczny sposób (basic authentication), to trzeba będzie zmodyfikować / rozbudować ten element aplikacji.
