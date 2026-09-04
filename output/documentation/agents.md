# Agentenmodell und Agentenaktionen

## Überblick

Ein Agent ist eine mobile Einheit der Liefer-Simulation. Er besitzt eine Position auf der Karte, einen Agententyp, eine Bewegungsgeschwindigkeit, eine Paketkapazität und einen Batteriestand. Zusätzlich speichert der Agent seine aktuelle Ladung, seinen Status und die zuletzt ausgeführte Aktion.

Die Agenten werden beim Zurücksetzen der Simulation erzeugt. Die Anzahl der Standard- und Express-Agenten wird aus `config/app.json` gelesen. Ihre Startpositionen werden zufällig aus freien, befahrbaren Straßenfeldern ausgewählt.

## Agententypen

Die Simulation verwendet zwei Agententypen:

| Typ | Geschwindigkeit | Kapazität | Maximale Batterie | Verbrauch pro Feld |
|---|---:|---:|---:|---:|
| Standard | 1 Feld/Tick | 3 Pakete | 100 EE | 2 EE |
| Express | 2 Felder/Tick | 1 Paket | 100 EE | 3 EE |

Die Werte werden nicht im Agenten-Code fest einprogrammiert, sondern aus `config/app.json` geladen. Dadurch können die Eigenschaften der Agententypen geändert werden, ohne die Simulationslogik anzupassen.

## Zustandsmodell

Das Datenmodell eines Agenten befindet sich in `app/domain/agent.py`.

| Attribut | Bedeutung |
|---|---|
| `id` | Eindeutige Identifikation des Agenten |
| `type` | Agententyp `Standard` oder `Express` |
| `position` | Aktuelle Position als Koordinate `(x, y)` |
| `speed` | Maximale Anzahl von Feldern pro Tick |
| `capacity` | Maximale Anzahl transportierbarer Pakete |
| `battery` | Aktueller Batteriestand |
| `battery_cost_per_field` | Konfigurierter Verbrauch pro Bewegungsfeld |
| `load` | Aktuelle Anzahl aufgenommener Pakete |
| `status` | Allgemeiner Status des Agenten |
| `last_action` | Zuletzt ausgewählte Aktion |

`last_action` wird in der Benutzeroberfläche in der Spalte **Aktion** angezeigt. So ist während der Simulation erkennbar, welche Aktion ein Agent zuletzt ausgeführt hat.

## Initialisierung

Beim Start oder Zurücksetzen der Simulation werden zunächst die Karte und anschließend die Agenten erzeugt. Für jeden Agenten wird abhängig vom Typ die passende Konfiguration ausgewählt:

- Standard-Agenten verwenden `agentTypes.standard`.
- Express-Agenten verwenden `agentTypes.express`.
- Die Startbatterie wird aus `batteryCapacity` übernommen.
- Geschwindigkeit, Kapazität und Batterieverbrauch werden ebenfalls aus der Konfiguration übernommen.
- Ein Agent wird nur auf einem freien und befahrbaren Straßenfeld platziert.

Wenn kein geeignetes Feld mehr frei ist, wird kein weiterer Agent erzeugt und eine Meldung im Simulationslog ausgegeben.

## Tickbasierte Hauptschleife

Die Simulation läuft in diskreten Ticks. In jedem Tick werden die Agenten in eine zufällige Reihenfolge gebracht. Dadurch erhält nicht immer derselbe Agent zuerst die Möglichkeit, eine Aktion auszuführen.

Für jeden Agenten wird anschließend eine Aktion ausgewählt und ausgeführt. Die Aktionsauswahl ist in Meilenstein 1 bewusst zufällig:

```python
# Meilenstein 1: In Meilenstein 2 durch die geplante Agentenaktion ersetzen.
action = self.choose_random_action()
self.execute_action(a, action, occupied, reserved)
```

Die Methode `choose_random_action()` ist die austauschbare Auswahlstrategie. In Meilenstein 2 kann sie durch eine geplante Agentenaktion, Nachrichtenverarbeitung oder Contract-Net-Logik ersetzt werden. Die eigentlichen Aktionsmethoden bleiben davon unabhängig bestehen.

## Verfügbare Aktionen

### Bewegung

Bei der Aktion `Bewegen` versucht der Agent, sich zufällig auf benachbarte, befahrbare Felder zu bewegen. Wände, bereits belegte Felder und im aktuellen Tick reservierte Felder werden ausgeschlossen.

Die Geschwindigkeit bestimmt die maximale Anzahl der Felder pro Tick:

- Ein Standard-Agent kann maximal ein Feld laufen.
- Ein Express-Agent kann maximal zwei Felder laufen.

Nach jedem Feld werden die möglichen Nachbarn neu ermittelt. Dadurch wird die aktuelle Position berücksichtigt. Wenn kein gültiges Nachbarfeld vorhanden ist, endet die Bewegung für diesen Tick.

Erreicht ein Agent während der Bewegung ein Depot oder ein Ziel, wird die Bewegung sofort beendet. Noch verfügbare Bewegungsfelder werden nicht genutzt. Der Agent bleibt bis zum nächsten Tick auf diesem Feld, damit Depot und Ziel als eigene Aktionspunkte behandelt werden können.

Die Bewegung ist in Meilenstein 1 zufällig. Es wird noch kein Weg zu einem bestimmten Ziel berechnet. Die A*-Wegsuche wird in einem späteren Meilenstein ergänzt.

### Paket aufnehmen

Ein Agent kann ein Paket nur aufnehmen, wenn alle folgenden Bedingungen erfüllt sind:

- Der Agent steht an der Depotposition des Tasks.
- Der Task besitzt den Status `open`.
- Die Kapazität des Agenten ist noch nicht ausgeschöpft.

Nach erfolgreicher Aufnahme:

- wird `load` um eins erhöht,
- erhält der Task den Status `in_transit`,
- wird die ID des Agenten in `assigned_agent_id` gespeichert.

Ist kein passendes Paket vorhanden oder ist die Kapazität erreicht, bleibt der Zustand unverändert. Die Situation wird im Nachrichtenlog angezeigt.

### Paket abliefern

Ein Agent kann ein Paket nur abliefern, wenn:

- der Task den Status `in_transit` besitzt,
- der Task diesem Agenten zugeordnet ist,
- der Agent an der Zielposition des Tasks steht.

Nach erfolgreicher Ablieferung:

- wird `load` um eins verringert,
- erhält der Task den Status `delivered`,
- wird eine Erfolgsmeldung im Log ausgegeben.

Steht der Agent nicht am richtigen Ziel oder besitzt er keinen passenden Task, wird keine Ablieferung durchgeführt.

### Nachricht senden

In Meilenstein 1 wird die Aktion `Nachricht senden` nur als Simulationsaktion protokolliert. Die Engine schreibt eine Meldung in das Log.

Eine echte Nachrichtenwarteschlange, Empfängerlogik und Nachrichtentypen wie `ANNOUNCE`, `BID` und `AWARD` werden in Meilenstein 2 ergänzt. Die Methode `send_message()` bildet dafür bereits einen klaren Erweiterungspunkt.

## Aktionen und Erweiterung für Meilenstein 2

Die Auswahl zufälliger Aktionen gehört nur zur ersten Entwicklungsstufe. Für Meilenstein 2 wird dieser Teil ersetzt:

```python
def choose_random_action(self):
    return self.r.choice((MOVE, PICKUP, DELIVER, SEND_MESSAGE))
```

Die ausführenden Methoden bleiben als fachliche Aktionen erhalten:

```text
move_agent()
pick_up_task()
deliver_task()
send_message()
```

Später entscheidet nicht mehr der Zufall, sondern eine Agenten- oder Contract-Net-Logik, welche Aktion sinnvoll ist. Dadurch kann die bestehende Aktionsausführung weiterverwendet werden.

## Anzeige in der Benutzeroberfläche

Die Benutzeroberfläche zeigt für jeden Agenten unter anderem:

- ID
- Typ
- Position
- letzte Aktion
- Batteriestand
- Kapazität
- aktuelle Ladung

Zusätzlich werden Aktionsmeldungen im Nachrichtenbereich angezeigt. Dadurch kann nachvollzogen werden, ob ein Agent sich bewegt, ein Paket aufgenommen, ein Paket abgeliefert oder eine Nachricht gesendet hat.

## Abgrenzung des aktuellen Entwicklungsstands

In Meilenstein 1 sind das Agentenmodell, die Initialisierung, die zufällige Bewegung, die Geschwindigkeiten und die grundlegende Paketaufnahme beziehungsweise Ablieferung umgesetzt.

Noch nicht vollständig umgesetzt sind:

- echte Nachrichtenübermittlung zwischen Agenten und Depot,
- Contract-Net-Ausschreibungen,
- A*-Wegplanung,
- automatische Auswahl einer sinnvollen Aktion,
- tatsächlicher Batterieverbrauch,
- Aufladen im Depot.

Diese Funktionen werden in den späteren Meilensteinen ergänzt. Die vorhandenen Aktionsmethoden und die Anzeige der letzten Aktion bilden dafür die Grundlage.
