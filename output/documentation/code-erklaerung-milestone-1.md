# Erklärung des Programmcodes

## Gesamtbild

Die Anwendung ist in mehrere Verantwortungsbereiche aufgeteilt:

- `main.py`: startet die Anwendung
- `config/`: enthält die Konfiguration
- `domain/`: enthält Agenten, Aufträge und Graphen
- `maps/`: erstellt Karten
- `simulation/`: steuert den Ablauf
- `ui/`: zeichnet die Oberfläche und verarbeitet Eingaben
- `tests/`: prüft zentrale Funktionen

## 1. Programmstart

In `main.py` passiert:

1. Der Pfad zur Anwendung wird bestimmt.
2. `config/app.json` wird geladen.
3. Ein `SimulationEngine` wird erstellt.
4. Die Pygame-Oberfläche `SimulatorApp` wird gestartet.

```python
config = load_config(...)
engine = SimulationEngine(config)
SimulatorApp(engine, config).run()
```

## 2. Konfiguration

`config.py` liest die JSON-Datei und wandelt sie in typisierte Konfigurationsobjekte um.

Dort stehen unter anderem:

- Kartentyp und Kartengröße
- Anzahl der Startagenten
- Geschwindigkeit und Kapazität
- Batteriekapazität und Verbrauch
- Ladedauer
- Fenstergröße und Tick-Geschwindigkeit

Dadurch sind Simulationsparameter vom Programmcode getrennt.

## 3. Karte und Graph

Die Karte wird als Graph modelliert. Jede Position `(x, y)` ist ein Knoten. Befahrbare Nachbarn werden über Kanten verbunden.

In `graph.py` gibt es:

- `GraphNode`
- `GraphMap`
- `NodeKind`

`NodeKind` unterscheidet:

- `ROAD`
- `WALL`
- `DEPOT`
- `TARGET`

`rebuild_edges()` verbindet ausschließlich horizontal und vertikal benachbarte befahrbare Felder. Wände erhalten keine Kanten.

Die festen Karten stehen in `presets.py`. Die Zufallskarte wird in `random_map.py` erzeugt. Dabei wird nach jedem Wandsegment geprüft, ob die begehbaren Felder weiterhin zusammenhängend sind.

## 4. Agenten

`agent.py` definiert den Agenten als Dataclass.

Ein Agent besitzt:

- ID
- Typ
- Position
- Geschwindigkeit
- Kapazität
- Batterie
- Ladung
- Status
- aktuelle Aktion
- verbleibende Lade-Ticks

Es gibt zwei Typen:

```python
AgentType.STANDARD
AgentType.EXPRESS
```

Die konkreten Werte kommen aus der Konfiguration. Standard-Agenten fahren langsamer, können aber mehr laden. Express-Agenten fahren schneller und verbrauchen mehr Energie.

## 5. Aufträge

`deliverytask.py` beschreibt einen Auftrag:

- Auftrag-ID
- Startdepot
- Lieferziel
- Erzeugungs-Tick
- Status
- zugewiesener Agent

Der Status verändert sich typischerweise so:

```text
open -> in_transit -> delivered
```

Beim Aufnehmen wird der Agent eingetragen und seine Ladung erhöht. Beim Abliefern wird die Ladung reduziert und der Auftrag abgeschlossen.

## 6. Simulations-Engine

Die zentrale Logik befindet sich in `engine.py`.

Beim Zurücksetzen:

- wird eine neue Karte erzeugt,
- der Tick auf `0` gesetzt,
- werden Agentenlisten und Nachrichten geleert,
- werden die konfigurierten Standard- und Express-Agenten erzeugt.

## 7. Ein Simulationsschritt

`engine.step()` entspricht einem Simulations-Tick.

Ablauf:

1. Prüfen, ob alle Agenten gestrandet sind.
2. Tick erhöhen.
3. Belegte Positionen erfassen.
4. Agenten in zufälliger Reihenfolge bearbeiten.
5. Gestrandete Agenten überspringen.
6. Ladephasen bearbeiten.
7. Batterie prüfen.
8. Depotregeln anwenden.
9. Eine Aktion auswählen.
10. Die Aktion ausführen.

Die zufällige Reihenfolge verhindert, dass immer derselbe Agent zuerst handelt.

## 8. Aktionsauswahl

`choose_random_action()` erkennt besondere Situationen:

- Gibt es am Depot einen offenen Auftrag, wird `PICKUP` gewählt.
- Befindet sich der Agent am passenden Ziel, wird `DELIVER` gewählt.
- Ansonsten wird zufällig zwischen `MOVE` und `SEND_MESSAGE` gewählt.

Die eigentliche Wegplanung ist also noch keine A*-Planung, sondern die zufällige Bewegungslogik aus Aufgabe 1.

## 9. Bewegung

`move_agent()`:

- liest die Nachbarknoten,
- entfernt belegte oder reservierte Positionen,
- verhindert unerlaubtes Betreten von Zielen,
- bewegt den Agenten höchstens `speed` Felder,
- reduziert pro Feld die Batterie,
- markiert Agenten bei leerer Batterie als `STRANDED`.

Ein Express-Agent kann deshalb in einem Tick bis zu zwei Felder fahren, ein Standard-Agent normalerweise nur eines.

## 10. Depots und Laden

Beim Erreichen eines Depots:

- wird ein passender Auftrag aufgenommen, wenn einer vorhanden ist,
- andernfalls beginnt die Ladephase.

`chargingDurationTicks` wird über `charging_ticks_remaining` umgesetzt. Während der Ladephase bewegt sich der Agent nicht. Erst nach Ablauf der konfigurierten Dauer wird die Batterie vollständig geladen.

## 11. Oberfläche

`app.py` enthält die Pygame-Oberfläche.

Die Oberfläche:

- zeichnet die Karte,
- stellt Wände, Depots und Ziele dar,
- zeigt Agenten farblich nach Typ,
- zeigt Batterie und Ladung,
- zeigt aktuelle Aktionen,
- zeigt Aufträge und Nachrichten,
- zeigt das vorbereitete Contract-Net-Log.

Die Oberfläche steuert nicht direkt die Simulation, sondern ruft Methoden des `SimulationEngine` auf.

Beispielsweise:

- `1`: Auto-Modus
- `2`: ein Tick
- `3`: Reset
- `4`: Standard-Agent hinzufügen
- `5`: Express-Agent hinzufügen
- `6`: Auftrag hinzufügen

## 12. Was bereits vorbereitet ist

Der Code enthält bereits Grundlagen für spätere Aufgaben:

- Graphstruktur für A*
- Contract-Net-Anzeige und Log
- Batteriemodell
- strukturierte Agenten- und Auftragsobjekte
- konfigurierbare Karten
- UI für spätere Kennzahlen
- Tests für Karten und Bewegungsregeln

Noch nicht vollständig umgesetzt sind:

- echtes Contract-Net-Verfahren
- A*-Wegplanung
- Prolog-Anbindung
- vollständige KPI-Erfassung
- echte Nachrichtenkommunikation zwischen Agenten

Das ist für Aufgabe 1 kein Problem. Die aktuelle Architektur ist bewusst so angelegt, dass diese Funktionen später ergänzt werden können, ohne die Grundstruktur neu zu bauen.
