# Symulacja Ewolucji Organizmów

## Opis Projektu
Aplikacja symuluje proces nauki i adaptacji osobników w dynamicznym środowisku. Głównym celem jest analiza zdolności organizmów do zdobywania zasobów i interakcji z otoczeniem. Projekt umożliwia dostosowanie parametrów symulacji oraz konfigurację ekosystemu według preferencji użytkownika. Użytkownik może określić lokalizację zasobów (pokarmu) oraz rozmieszczenie barier, które wpływają na ewolucję populacji. Dane zbierane w trakcie symulacji są zapisywane w pamięci lokalnej urządzenia i mogą być poddane wizualizacji oraz analizie po zakończeniu procesu.

## Instalacja i uruchomienie aplikacji

Użytkownik ma dwie możliwości instalacji programu:

1. **Instalacja pliku wykonywalnego**  
   Pierwsza opcja polega na pobraniu pliku instalacyjnego w formacie `.exe`, który jest dostępny pod adresem: [LINK](LINK). Po pobraniu pliku należy go otworzyć i przejść do instrukcji użytkowania. Program jest gotowy do użycia.

2. **Instalacja z wykorzystaniem repozytorium GitHub**  
   Druga opcja zakłada pobranie kodu aplikacji bezpośrednio z repozytorium dostępnego na GitHubie. Proces ten wymaga wykonania kilku kroków, które zostały szczegółowo opisane w poniższym przewodniku.

### Instalacja z wykorzystaniem repozytorium GitHub

1. **Zainstalowanie środowiska Python**  
   Upewnij się, że na Twoim systemie operacyjnym jest zainstalowany Python, ponieważ jest to język programowania, w którym stworzono tę aplikację. Zalecane są najnowsze wersje Pythona i PIP, ale wymagane minimalne są `python-3.13` oraz `pip-24.3.1` odpowiednio. W niniejszym przewodniku zakładamy korzystanie z wiersza poleceń (`cmd`). Należy zwrócić uwagę na różnice w użyciu ukośników w poleceniach: `\` dla systemu Windows oraz `/` dla systemów Linux.

2. **Sklonowanie repozytorium projektu lub pobranie pliku ZIP**    
   Jeśli zdecydujesz się na sklonowanie projektu, możesz to zrobić za pomocą następującego polecenia:

   ```sh
   git clone https://github.com/AgEwa/Ewolucja project_name
   ```

   Jeśli zdecydowałeś się na pobranie pliku ZIP, rozpakuj go do wybranego folderu.  
   W powyższym przykładzie zakładamy, że projekt zostanie umieszczony w katalogu o nazwie `project_name`.

3. **Przejście do katalogu projektu**  
   Aby przejść do folderu zawierającego pliki projektu, użyj poniższego polecenia:

   ```sh
   cd project_name
   ```

4. **Instalacja wirtualnego środowiska Pythona**  
   W celu uniknięcia globalnej instalacji pakietów, zaleca się utworzenie wirtualnego środowiska:

   ```sh
   python -m venv .venv
   ```

5. **Aktywacja wirtualnego środowiska**  
   Aktywuj utworzone wcześniej środowisko za pomocą następującego polecenia:

   ```sh
   .venv\Scripts\activate
   ```

   Po pomyślnej aktywacji, na początku wiersza poleceń powinien pojawić się wskaźnik `(.venv)`, potwierdzający uruchomienie środowiska wirtualnego.

6. **Instalacja wymaganych zależności**  
   Zainstaluj wszystkie wymagane pakiety, korzystając z pliku `requirements.txt`:

   ```sh
   pip install -r requirements.txt
   ```

7. **Uruchomienie aplikacji**  
   Aby uruchomić aplikację, wykonaj następujące polecenie:

   ```sh
   python app.py
   ```

   Aplikacja zostanie uruchomiona w graficznym interfejsie użytkownika.

8. **Zakończenie działania aplikacji**  
   Po zamknięciu głównego okna aplikacji i zakończeniu wszystkich procesów symulacji, odpowiednia informacja zostanie wyświetlona w wierszu poleceń.

9. **Dezaktywacja wirtualnego środowiska**  
   Aby opuścić wirtualne środowisko, wykonaj poniższe polecenie:

   ```sh
   deactivate
   ```


