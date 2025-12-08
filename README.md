# fencing_app
24.11.2025
- navázání na další big project = vizualizace turnajů a další statistiky (původně jen Plotlym později DashApp)

Základní setup:
- aplikace v Django
- Sqlite DB
- administrace na zakládání a spravování účtů
- účty pro 20 lidi
- hlavní menu se záložkami - fixed on top
- toggle na noční režim

Funkce (jednotlivé stránky):
- O mně:
    - jméno
    - klub (vyberu si ze seznamu)
    - seznam zůčastnění na turnajích (vyberu si ze seznamu)
    - základní statistika
- Statistiky:
    - podrobnější statistiky z turnajů individuální
    - Klub = za všechny ostatní ze stejného klubu, vlastní tabulka, Interní miniturnaje
- Tréninky:
    - Poznámky z tréninků = prostor pro poznámky a postřehy
    - Kruháče = uložené sestavy na cvičení (private/sdílet) + nahrané songy a jejich přehrávání ke kruháči
- Fotky z akcí = výběr toho nejlepšího, nahráno námi
- Kalendář akcí = kopie toho na czechfencing + upozornění na ně + reakce ostatních kolegů
- Stav placení příspěvků = QR kod na platbu + velké upozornění
- Návody:
    - slovníček pojmů
    - Videa na ytb
    - pravidla výcuc
    - Skladba kord - 3D model hrotu + návod na výlep + seznam nářadí
- Vybavení = figura šermíře se veškerým vybavením + orientační cena a prokliky na nákup + možnost si odškrtávat nakoupené vybavení

POZN:
- při importu z excelu se existující šermíři/události/výsledky updatují, přepíšou

TODO:

- bodíky za turnaj - pitomý sloupec se neukazuje na jedné tabulce - Klubs

- nastavit ENV pro změnu hesla přes mail..jinak nevím jak obnovit account - nebo je to ok protože se vše sbírá na fencera a ne usera?

- zvýraznit a nechat svítit 1-3 místa, což měla teď Kristýna v Brně

dodělat opravdové turnaje 2025 a 2024 - viz nový zdroj dat !!

- Statistiky - přidat totaly nebo průměry, a filtry

WIKI -  doplnit materiály a URLs, fotka hrotu atd

Masíčko - začít řešit tu hudbu jak chtěl Tonda