# GMSExtract

### Description
This script is intended to be used for extracting the H-/P-/EUH-Statements
from chemicals' safety data sheets. The extracted Statements will be returned
as TAB-separated Lists of the COMMA-separated statements in order of their discovery
within the input. e.g.
```
H319, H335, H315	P261, P302 + P352, P280, P305 + P351 + P338, P271	EUH061
```

Input may be the path to a pdf file, finished with an empty input line.
If a path to a pdf file was recognized the program will confirm, that the input will be interpreted as such.
```
> aceton.pdf
>

Interpreting input as path of pdf file.
```

Input may alternatively be the entire safety data sheet as text, finished with an empty input line.
```
> Sicherheitsinformationen gemäß GHS Gefahrensymbol(e)￼
> Gefahrenhinweis(e)
> H315: Verursacht Hautreizungen.
> H319: Verursacht schwere Augenreizung.
> H335: Kann die Atemwege reizen.
> Sicherheitshinweis(e)
> P261: Einatmen von Staub/ Rauch/ Gas/ Nebel/ Dampf/ Aerosol vermeiden.
> P271: Nur im Freien oder in gut belüfteten Räumen verwenden.
> P280: Schutzhandschuhe/ Augenschutz/ Gesichtsschutz tragen.
> P302 + P352: BEI BERÜHRUNG MIT DER HAUT: Mit viel Wasser waschen.
> P305 + P351 + P338: BEI KONTAKT MIT DEN AUGEN: Einige Minuten lang behutsam mit Wasser spülen.
> Eventuell vorhandene Kontaktlinsen nach Möglichkeit entfernen. Weiter spülen.
> Ergänzende Gefahrenhinweise EUH061
> SignalwortAchtungLagerklasse10 - 13 Sonstige Flüssigkeiten und
> FeststoffeWGKWGK 1 schwach wassergefährdendEntsorgung3
>
```

### Versions

Python: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3.8.5 <br>
pdfminer.six: &nbsp;&nbsp; 20201018
