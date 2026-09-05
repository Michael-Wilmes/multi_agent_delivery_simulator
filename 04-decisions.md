## 31.08.2026 ## 
### Gedanken vor Beginn der Implementierung

Bevor ich mit der eigentlichen Implementierung begonnen habe, habe ich zunächst die komplette Aufgabenstellung gelesen und versucht, die einzelnen Teilaufgaben im Zusammenhang zu betrachten. Dabei war mir wichtig, nicht jede Aufgabe isoliert umzusetzen, sondern bereits früh Entscheidungen zu treffen, die auch für spätere Aufgaben sinnvoll sind.

Für die grafische Oberfläche habe ich mich für Pygame entschieden. Grundsätzlich könnte die Simulation auch über die Konsole umgesetzt werden. Da jedoch Agenten, Aufträge, Hindernisse und später auch Bewegungen sowie Auktionsprozesse visualisiert werden sollen, erschien mir eine grafische Darstellung deutlich verständlicher und intuitiver. Gleichzeitig ist Pygame eine etablierte Python-Bibliothek, für die zahlreiche Beispiele und Dokumentationen verfügbar sind.

Nachdem ich alle Aufgaben gelesen hatte, fiel mir auf, dass in Aufgabe 3 die Verwendung eines Graphen gefordert wird. Statt zunächst eine klassische Rasterstruktur zu implementieren und diese später wieder umzubauen, habe ich mich entschieden, von Anfang an auf einer Graphenstruktur aufzubauen.

Jede Zelle der Karte wird dabei durch einen Knoten repräsentiert, während die Verbindungen zu den Nachbarzellen als Kanten modelliert werden. Dadurch entsteht zwar zu Beginn etwas mehr Aufwand, jedoch vermeide ich spätere Umbauten und schaffe bereits die Grundlage für die spätere Implementierung des A*-Algorithmus.

Ein weiterer Punkt betrifft die in Aufgabe 5 geforderten Kennzahlen (KPIs). Aus meiner Sicht ist es deutlich sinnvoller, relevante Ereignisse bereits während der Entwicklung zu erfassen, anstatt die benötigten Messgrößen erst am Ende nachträglich in den Code einzubauen. Deshalb habe ich mich entschieden, von Beginn an ein einfaches Ereignis- und Logging-Konzept vorzusehen.

Ereignisse wie das Erzeugen von Agenten, das Laden einer Karte, das Anlegen von Aufträgen oder später auch Gebote und abgeschlossene Transporte können dadurch direkt protokolliert werden. Diese Daten bilden anschließend die Grundlage für die Auswertung mit Pandas und die Visualisierung mit Seaborn.

Auch bei der Architektur habe ich versucht, möglichst früh eine saubere Trennung der Verantwortlichkeiten vorzusehen.

- Die Karte wird unabhängig von der Darstellung in einer eigenen Graphenstruktur verwaltet.
- Die grafische Oberfläche ist ausschließlich für die Visualisierung zuständig.
- Agenten, Aufträge und weitere Objekte erhalten eigene Klassen, auch wenn diese zu Beginn teilweise noch leer bleiben.

Dadurch kann die Funktionalität schrittweise erweitert werden, ohne dass die bestehende Struktur grundlegend angepasst werden muss.

Zusammenfassend bestand mein Ziel darin, bereits vor der ersten Zeile produktiven Codes Entscheidungen zu treffen, die spätere Erweiterungen berücksichtigen. Dadurch soll vermieden werden, dass bereits implementierte Komponenten zu einem späteren Zeitpunkt vollständig umgebaut werden müssen.

Insbesondere die Entscheidung für Pygame, die frühzeitige Verwendung einer Graphenstruktur sowie die direkte Berücksichtigung der KPI-Erfassung sollen dazu beitragen, den Gesamtaufwand während der weiteren Entwicklung zu reduzieren und eine nachvollziehbare Architektur aufzubauen.

---

## 03.09.2026 
## Wegberechnung

Da in der Aufgabenstellung die Manhattan-Distanz verwendet wird und keine diagonalen Bewegungen beschrieben werden, wird angenommen, dass Agenten ausschließlich horizontale und vertikale Bewegungen ausführen können.

Erlaubte Bewegungen:

```text
↑
← →
↓
```

Die Kosten einer Bewegung betragen unabhängig von der Richtung 1.

Die Pfadlänge entspricht somit der Anzahl der tatsächlich zurückgelegten Felder.

---

## Bewegungsregeln der Agenten

Die folgenden Regeln sind im aktuellen Simulationskern umgesetzt:

### Allgemeine Bewegung

- Agenten bewegen sich ausschließlich auf begehbaren, verbundenen Nachbarknoten.
- Diagonale Bewegungen sind nicht erlaubt. Pro Bewegungsschritt wird nur ein horizontaler oder vertikaler Nachbar gewählt.
- Die möglichen Nachbarfelder werden zufällig ausgewählt.
- Ein Standard-Agent bewegt sich höchstens ein Feld pro Tick.
- Ein Express-Agent bewegt sich höchstens zwei Felder pro Tick.
- Die tatsächliche Anzahl der Felder kann geringer sein, wenn kein zulässiges Nachbarfeld verfügbar ist.
- Bereits von einem anderen Agenten belegte Felder dürfen nicht betreten werden.
- Ein Feld, das im aktuellen Tick bereits für einen anderen Agenten reserviert wurde, darf ebenfalls nicht betreten werden.
- Nach jedem tatsächlich zurückgelegten Feld wird der Batterieverbrauch abgezogen.

### Sonderregeln für Depots und Ziele

- Hält ein Agent an einem Depot oder Ziel an und führt innerhalb desselben Bewegungsvorgangs keine weiteren Felder aus.
- Kommt ein Agent ohne offenen Auftrag auf ein Depot, wird unmittelbar die aktuelle Aktion `Batterie laden` angezeigt. => Das gilt nur für Aufgabe 1
- Kommt ein Agent auf ein Depot, an dem er einen Auftrag aufnehmen kann, wird der Auftrag unmittelbar aufgenommen und die aktuelle Aktion `Lieferung aufnehmen` angezeigt.
- Im Tick nach `Lieferung aufnehmen` greift der Ladealgorithmus: Die aktuelle Aktion lautet `Batterie laden` und der Agent wartet diesen Tick.
- Beim Aufenthalt auf einem Depot ohne Auftrag wird ebenfalls im folgenden Tick geladen und gewartet.
- Das Betreten des Depots löst die Batterieladung nicht  selben Tick aus.
- Die Batterie wird im Ladevorgang vollständig auf die konfigurierte Kapazität gesetzt.
- Die Anzahl an Ticks, die der Lafevorgang benötigt kann konfiguriert werden.
- Im Tick, in dem `Loading` gesetzt wird, darf der Agent keine Bewegung ausführen. Andere Aktionen, insbesondere das Aufnehmen eines Pakets, bleiben möglich.
- Die aktuell ausgeführte Aktion wird über `current_action` dargestellt;
- Ein Ziel darf nur betreten werden, wenn der Agent einen eigenen Auftrag im Status `in_transit` besitzt.
- Ohne passenden Auftrag werden Zielknoten bei der Berechnung möglicher Bewegungen ausgeschlossen.
- Eine Zustellung ist nur auf einem Ziel und nur für einen passenden Auftrag des Agenten möglich.

### Kollisionen und leere Batterie
- Erreicht die Batterie nach einer Bewegung den Wert `0`, wird der Agent als `Stranded` markiert.
- Ein gestrandeter Agent bewegt sich nicht mehr und bleibt als belegtes Hindernis auf seiner Position stehen.
- Sind alle Agenten gestrandet, wird die Simulation angehalten.

### Ladezeitpunkt

Die Konfiguration enthält den Parameter `chargingDurationTicks`. Im aktuell implementierten Bewegungsablauf wird jedoch nur ein Lade-Tick berücksichtigt: Das Laden beginnt im Tick nach dem Aufenthalt im Depot und setzt die Batterie vollständig auf. Eine mehrtickige Ladephase entsprechend dem konfigurierten Wert ist noch nicht umgesetzt.

---

## Standard- und Express-Agenten

Die Unterschiede zwischen Standard- und Express-Agenten sind in der Aufgabenstellung nicht eindeutig beschrieben.  
Daher werden folgende Annahmen getroffen.

### Standard-Agent

- geringere Geschwindigkeit
- höhere Transportkapazität
- geringerer Energieverbrauch

### Express-Agent

- höhere Geschwindigkeit
- geringere Transportkapazität
- höherer Energieverbrauch

Die konkreten Werte werden über die Konfigurationsdatei definiert.

---

## Batteriemodell

Die Aufgabenstellung fordert, dass jeder Agent über einen Batteriestand verfügt. Konkrete Vorgaben zum Verbrauchs- oder Lademodell werden jedoch nicht gemacht.

Daher wird ein einfaches Energiemodell verwendet, das die Auftragsvergabe und Bewegungsplanung beeinflusst, ohne die Komplexität der Simulation unnötig zu erhöhen.

### Batterieverbrauch

Für die Simulation wird eine idealisierte Welt angenommen. Jedes tatsächlich
zurückgelegte Feld verursacht einen konstanten Energieverbrauch, der nur vom
Agententyp abhängt. Die Anzahl der transportierten Pakete verändert den Verbrauch
nicht.

Diese Vereinfachung wurde bewusst gewählt, um die Batterieberechnung überschaubar und
deterministisch zu halten. Dadurch kann dieselbe Kostenlogik später direkt bei der
A*-Wegsuche und bei der Prüfung der Reichweite verwendet werden. Auch die Prolog-
Abfrage `is_reachable/2` bleibt klar von der agentenspezifischen Energieberechnung
getrennt: Sie prüft nur, ob grundsätzlich ein Weg existiert.

Die Batterie reduziert sich linear mit der tatsächlich zurückgelegten Strecke:

```text
BatterieNeu =
BatterieAlt -
(GefahreneFelder * VerbrauchProFeld)
```

Es werden keine zusätzlichen Effekte berücksichtigt, wie beispielsweise:

- Anzahl der transportierten Pakete
- unterschiedliche Straßen- oder Feldtypen
- Verkehrsaufkommen oder Staus
- Batterietemperatur
- Batteriealterung
- Nichtlineare Entladekurven
- Verbrauchsänderungen durch niedrigen Ladestand
- Geschwindigkeitsänderungen durch niedrigen Ladestand

### Laden

Batterien können ausschließlich in Depots geladen werden.  
Befindet sich ein Agent in einem Depot, startet automatisch ein Ladevorgang.

Die Dauer des Ladevorgangs wird über die Konfigurationsdatei definiert.

```text
chargingDurationTicks
```

Nach erfolgreichem Abschluss des Ladevorgangs wird die Batterie vollständig geladen.

```text
Batterie = Batteriekapazität
```

### Auftragsannahme

Ein Agent darf einen Auftrag nur dann annehmen, wenn ausreichend Energie vorhanden ist, um:

1. das auftraggebende Depot zu erreichen,
2. den Auftrag vollständig auszuführen,

Zusätzlich wird eine Sicherheitsreserve berücksichtigt.

Formal:

```text
BatterieAktuell >=
Energie(Position -> Depot)
+ Energie(Depot -> Ziel)
+ Sicherheitsreserve
```

Ist diese Bedingung nicht erfüllt, gibt der Agent kein Gebot für den Auftrag ab.

Dadurch wird verhindert, dass Agenten Aufträge annehmen, die sie nicht vollständig ausführen können.

### Verhalten nach einer Lieferung

Nach Abschluss eines Auftrags wird der aktuelle Batteriestand geprüft.

Falls die verbleibende Energie nicht mehr ausreicht, um weitere Aufträge sicher ausführen zu können, fährt der Agent automatisch zum nächstgelegenen erreichbaren Depot und lädt dort seine Batterie auf.

### Verhalten ohne Auftrag

Hat ein Agent keinen offenen oder zu transportierenden Auftrag, wartet er an
seiner aktuellen Position und bewegt sich nicht zufällig.

Befindet sich der Agent in einem Depot und ist seine Batterie nicht vollständig
geladen, lädt er dort automatisch. Bei vollständig geladener Batterie bleibt
der Agent im Zustand `Idle`, bis ein neuer Auftrag verfügbar ist.

Eine automatische Fahrt zu einem Depot ohne Auftrag findet nicht statt, da sie
unnötig Energie verbrauchen würde.

### Leere Batterie

Ein Agent sollte durch die Reichweitenprüfung vor der Auftragsannahme niemals während eines regulären Auftrags vollständig entladen werden.

Erreicht die Batterie dennoch den Wert 0, gilt:

```text
Status = STRANDED
```

Der Agent bleibt auf seiner aktuellen Position stehen und stellt ein Hindernis für andere Agenten dar.
Diese Fälle werden als KPI erfasst und ausgewertet.

---

## Konfiguration

Folgende Parameter werden über eine Konfigurationsdatei definiert:

- Geschwindigkeit pro Agententyp
- Transportkapazität pro Agententyp
- Batteriekapazität
- Energieverbrauch pro Feld
- Ladedauer im Depot
- Sicherheitsreserve

Beispiel:

```json
{
  "agentTypes": {
    "standard": {
      "speed": 1,
      "capacity": 3,
      "batteryCapacity": 100,
      "batteryCostPerField": 2
    },
    "express": {
      "speed": 2,
      "capacity": 1,
      "batteryCapacity": 100,
      "batteryCostPerField": 3
    }
  },
  "battery": {
    "chargingDurationTicks": 2,
    "reserve": 10
  }
}
```

Die Werte stellen Simulationsparameter dar und sind keine physikalischen Messwerte.


## Dokumentation  
Die HTML-Dokumentation wurde aus den projektbegleitenden Markdown-Dateien generiert. Sie enthält ein verlinktes Inhaltsverzeichnis und kann direkt offline im Browser geöffnet werden.