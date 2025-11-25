# fencing_app
24.11.2025
- navázání na další big project = vizualizace turnajů a další statistiky (původně jen Plotlym později DashApp)

Základní setup:
- aplikace v Django
- Sqlite DB
- administrace na zakládání a spravování účtů
- účty pro 20 lidi
- hlavní menu se záložkami
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

TODO:
- O mně - Účast na turnajích oříznout na menší tabulku, bez skore, max pořadí, ale ukázat i šedivě turnaje co byly a já tam nebyl
- O mně - Účast na turnajích - sám si zakliknu, kde jsem byl podle seznamu, a pořadí
- Statistiky - přidat totaly nebo průměry, a filtry
- počítat i body, společná tabulka?
- Statistiky - já vs klub - toggle button
- Statistiky - ...
- interní miniturnaje - ukazovat stejná data jko u turnajů