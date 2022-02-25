# Opendata MŽP

Platforma pro zpracování OpenData ze zdrojů MUZO na MŽP

## Jak to funguje?

Součástí platformy jsou tyto komponenty:

1. **Elasticsearch** - pro uložení konsolidovaných dat
2. **Kibana** pro prohlížení konsolidovaných dat
3. **Imex** - pro import a tranformaci dat ze zdroje typu MUZO a pro export dat do datasetu CSV

### Import dat do elasticsearch

Pro import, transformaci a uložení dat se používá nástroj **logstash** platformy ELK. Pro každý dataset existuje 
jedna "roura" logstash a jeden index nebo sada indexů elasticsearch. 

Roura má tři části: 
- **vstup** - Identifikuje vstupní datový zdroj, konfiguruje JDBC driver a patřičná SELECT. 
- **filtr** - provádí tranformaci a základní konsolidaci dat. Například sjednocuje názvy polí. 
- **výstup** - zajišťuje uložení dat do elasticsearch
 
Import se pouší pomocí služby **cron**

### Export dat do CSV

Pro vlastní export a výběr a úpravu datových položek se používá skript v jazyce **Python 3**. 
V rámci exportního skriptu se načtou data z relevantního indexu elasticsearch a provede se jejich převod 
do podoby vhodné pro export do CSV. To znamená: 
- vyberou se relevantní atributy uložených datových objektů
- časové položky se převedeou z UTC do lokální časové zóny a ořízne se časový údaj
- z textových položek se odstraní znaky nových řádků
- doplní se společné atributy

Takto vytvořený řádek se uloží do souboru CSV. 

Soubor CSV se doplní o BOM a uloží na dohodnuté místo. 

##  Konfigurace

Celá platforma je konfigurovatelná pomocí systémových proměnných 

- **CSV_OUTPUT_DIRECTORY** - adresář pro uložení výsledných CSV souborů
- **ES_HOST** - hostitel elasticsearch. Implicitně *localhost:9200*
- **ES_VERSION** - verze ELK (optimalizováno pro 6.8.7, poslední 7.6.1)         

## Spuštění 

Importní a exportní skripty se spouštění pomocí služby **cron**. V souboru **crontab** je uveden způsob volání 
importních a exportních skriptů.

## Docker

TBD
