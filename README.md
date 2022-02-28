# Opendata MŽP

Platforma pro zpracování OpenData ze zdrojů **MUZO JASU** na MŽP

## Jak to funguje?

Součástí platformy jsou tyto komponenty:

1. **elasticsearch** - pro uložení konsolidovaných dat
2. **kibana** pro prohlížení konsolidovaných dat
3. **jasu** - pro import a tranformaci dat ze zdroje typu MUZO a pro export dat do datasetu CSV

### Import dat do elasticsearch

Pro import, transformaci a uložení dat se používá skript v jazyce **Python 3**. 
V rámci skriptu se na základě konfigurace načtou data z datového zdroje, provede se jejich transformace
a uloží se do datového jezera **elasticseach**. 

Nástroj **logstash** platformy ELK se už nepoužívá.

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

## Spouštění

Byly vytvořeny tři typy importních a exportních úloh: 
- **import_all**: Importuje na základě konfigurace všechny datové zdroje **JASU**.
- **export_all**: Vytvoří kompletní CSV datasety pro všechny organizace a všechny typy dokumentů.
- **export_yyyy**: Vytvoří CSV datasety pro všechny organizace a všechny typy dokumentů pro jeden rok. 

##  Konfigurace

Konfigurace služby se provádí jednak pomocí systémových proměnných:
- **ES_HOST_NAME**: hostname master node clusteru elasticseach (elasticseach)
- **ES_PROTOCOL**: přenosový protokol (http)
- **ES_PORT**: TCP port endpointu (9200)
- **ES_USER**: Uživatel elasticsearch ()
- **ES_PASSWORD**: Přístupové heslo elasticsearch ()

a jednak pomocí konfiguračního souboru **opendata.yml**. 

## Spuštění 

Importní a exportní skripty se spouštění v rámci frameforku Flask na pozadí. Plánovač 
je dostupný pomocí REST API rozhraní na URL http://hostname:8080/scheduler 
(viz [dokumentace](https://viniciuschiele.github.io/flask-apscheduler/rst/api.html))

## Docker

Obraz Docker se vytvoří 

    docker build -t sysnetcz/opendata-jasu:version .
