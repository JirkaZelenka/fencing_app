
DONE: přepsat do skills
- napojení na exitující účty - s propmptem na potvrzení + Rok narození
- líp udělat ten seznam, jen jména + stav napojení -> případně zámeček.
- badges pro uživatele -> využiji i v HpoP
- základy angličtiny, switch
- articles + text managment, velmi solidní !!
- uploading profile photo
- using R2 storage (přidat i do obsidianu, místo NAS)
- using PC + wake on Lan + Termius -> hosting dashboard app na 0.0.0.0:X + tailscale = z mobilu se tam připojím.
- přidat přidání hotové deploynuté appky na app_dashboard jako krok do deploymentu na app_dashboard :)
- tagy u fotek na vyhledávání lidí

Important info:
Added. You now have a translation sync command:
New file: fencers/management/commands/sync_translations.py
Command: python manage.py sync_translations


##########################################
TODO:

- bodíky za turnaj - pitomý sloupec se neukazuje na jedné tabulce - Klubs

dodělat opravdové turnaje 2025 a 2024 - viz nový zdroj dat !!

- Statistiky - přidat totaly nebo průměry, a filtry

Masíčko - začít řešit tu hudbu jak chtěl Tonda
Masíčko - možnit drag and drop při tvrobě listu, na řazení. lepší i pro mobil

- vybavení = rozpadnout sekci nářadí na spoustu malých políček, použít foto mojí krabice jako referenci.

DB je na to ready. ale chybí to vyplnění cen u Ruby a 5M co předtím bylo. nahrát, a udělat dump data. prokliky pak skoro fungují.

Badges: co přidat ještě "pokročilý", aby každý byl něco? 
a R a A "Král a Královna" - korunku?
a přidat pohár/medaile pro ty, co nedávno něco vyhráli !
-> přidat někam legendu

- bug: ve statistikách se ukazuje opět user name místo Fencer name

- bug: proklik na nákup výbavy se stackuje za URL

- kde všude notifikační blikání? nový požadavek platby, Novinka, Kalendář?

- soupis turnajů - na jakých stránkách je co, co je žebříček, UŠL, padavky a sokolí péro, veteráni, akademičky, Fencing time live

-  Ostatní akce = soustředění, workshop, Sportovní den, úklid kanclu, ... teoreticky vše, co je oficiální, pro všechny.

- od Oty sehnat Videa na yt, od Vince grafiku

-> přesun do Tournamnet app - až dodělám možnost z fotky předvyplnit pools, tak budu moci poměrně snadno přenést historické turnaje do hotových.
jinak hotové turnaje chci nahrávat i jinak, z histoirických dat a mých statistik = 4. app (tato humanitní, tournamenty - organizační, souboje = mini app, a pak statistiky globál)