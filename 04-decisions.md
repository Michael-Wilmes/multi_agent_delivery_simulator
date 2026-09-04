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

## Standard- und Express-Agenten

Die Unterschiede zwischen Standard- und Express-Agenten sind in der Aufgabenstellung nicht eindeutig beschrieben. Daher werden folgende Annahmen getroffen.

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

Die Batterie reduziert sich linear mit der tatsächlich zurückgelegten Strecke.

```text
BatterieNeu =
BatterieAlt -
(GefahreneFelder * VerbrauchProFeld)
```

Es werden keine zusätzlichen Effekte berücksichtigt, wie beispielsweise:

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
3. anschließend wieder ein Depot zu erreichen.

Zusätzlich wird eine Sicherheitsreserve berücksichtigt.

Formal:

```text
BatterieAktuell >=
Energie(Position -> Depot)
+ Energie(Depot -> Ziel)
+ Energie(Ziel -> Depot)
+ Sicherheitsreserve
```

Ist diese Bedingung nicht erfüllt, gibt der Agent kein Gebot für den Auftrag ab.

Dadurch wird verhindert, dass Agenten Aufträge annehmen, die sie nicht vollständig ausführen können.

### Verhalten nach einer Lieferung

Nach Abschluss eines Auftrags wird der aktuelle Batteriestand geprüft.

Falls die verbleibende Energie nicht mehr ausreicht, um weitere Aufträge sicher ausführen zu können, fährt der Agent automatisch zum nächstgelegenen erreichbaren Depot und lädt dort seine Batterie auf.

### Leere Batterie

Ein Agent sollte durch die Reichweitenprüfung vor der Auftragsannahme niemals während eines regulären Auftrags vollständig entladen werden.

Erreicht die Batterie dennoch den Wert 0, gilt:

```text
Status = INAKTIV
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

Durch die verpflichtende Rückkehr zu einem Depot wird sichergestellt, dass die Batteriekapazität einen direkten Einfluss auf:

- die Auftragsvergabe,
- die Reichweitenplanung,
- die Verfügbarkeit von Agenten und
- die Bewegungsplanung

hat, ohne daraus ein eigenständiges Batteriemanagementsystem zu machen.


## Dokumentation  
Die HTML-Dokumentation wurde aus den projektbegleitenden Markdown-Dateien generiert. Sie enthält ein verlinktes Inhaltsverzeichnis und kann direkt offline im Browser geöffnet werden.