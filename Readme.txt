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
do osobnego serwisu, gdyż korzysta z niej silnie jedocześnie interfejs główny,
jak i interfejs kuriera.

Punkty trzeciego kamienia milowego, które nie zostały (jeszcze) zrealizowane:
4. Przygotować osobny interfejs (moduł / aplikację – osobny serwis, czyli prawdopodobnie osobny Dockerfile), który będzie symulował interfejs paczkomatu. Aplikacja do obsługi paczkomatu teraz ma pozwalać na dwa kroki:		
* wkładać paczki przez nadawcę, co oznacza podanie identyfikatora paczki z listu przewozowego podczas umieszczania jej w paczkomacie (później sobie to trochę lepiej zabezpieczymy);
* wyjmować paczkę / paczki przez kuriera.
Wyjmowanie paczki odbywa się w taki sposób, że kurier w swojej aplikacji podaje identyfikator paczkomatu. Jeżeli poda prawidłowy identyfikator, to w odpowiedzi uzyska unikalny token (ważny przez minutę). Uzyskany token musi wpisać w paczkomacie. W wyniku tego działania paczkomat wyświetli listę wszystkich paczek, które są do odebrania. Kurier zaznacza paczki, które chce odebrać i zapisuje zmiany. Zapisanie zmian jest jednoznaczne z wyjęciem paczek przez kuriera. W wyniku tej operacji zaznaczone paczki powinny zmienić swój status.
6. Aplikacja do obsługi paczkomatu ma być aplikację responsywną (dobrze wyświetlać się na ekranach z rozmiarami przypominającymi tablety różnej wielkości).
7. Aplikacja dla kuriera ma być aplikacją progresywną z możliwością instalacji na urządzeniu mobilnym. Aplikacja dla kuriera ma się dobrze wyświetlać na trzech typowych ekranach (monitor komputera, tablet, smartphone).
11. Proszę pamiętać, że może być kilka paczkomatów, a każdy z nich ma tylko „swoje” paczki. I tylko te wybrane paczki można odebrać z paczkomatu. Z tego względu w interfejsie / aplikacji do obsługi paczkomatu należy dodać pole wyboru aktualnie obsługiwanego paczkomatu. W rzeczywistości byłoby tak, że ta wartość byłaby z góry przypisana do aktualnego urządzenia, ale w naszych warunkach umówmy się, że podczas wkładania / wyjmowania paczki z paczkomatu trzeba jeszcze podać identyfikator paczkomatu, którego używamy.
16. Zasadne jest przygotowanie Swagger-a, który będzie umożliwiał wykonanie wszystkich kroków bez bezpośredniego korzystania z interfejsu przygotowywanych stron.
