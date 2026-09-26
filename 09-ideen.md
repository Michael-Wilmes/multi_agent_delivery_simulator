## Bewegung der Agenten: 
Jeder Agent, der eine Lieferung an einem Zielort abgegeben hat, muss diesen 
nach der Lieferung wieder verlassen, damit es keine Kollisionen mit anderen Agenten geben kann. 
Auf einem Feld kann immer nur ein Agent stehen

## Depots: 
Depots müssen eine Liste führen, welche Lieferungen abgeholt wurde und welche eventuell nicht. 
Zum Beispiell  wei es keine Gebote auf dieses Paket gab, welches in der Deadline-Zeit abgegeben wurde. 

## Zuschlag für Gebote: 
Der zuschlag für Ausgeschriebene Lieferungen wird am  Deadline Tick berechnet. 
Das ist aus Gründen der "Fairness", damit nicht der erste günstige Ageng gewinnt. 
Gibt es zu diesem Tick kein Gebot, sendet der Contract Manager die Message NO-BID  
und diese Lieferung wird als nicht geliefert markiert. 

## Bieten auf  Ausschreibungen: 
Wenn ein Agent bereits Aufträge in seiner Liste hat, ist der Startpunkt der Berechnung
das Ziel der letzten Lieferung. 
Dabei muss ebenfalls die Batterie - Kapazität am Ziel im Voraus berechnet werden. 


## Ideen zur späteren Simulationsauswertung (Aufgabe 5) 
Für die vollständige Simulation sollen unterschiedliche Szenarien mit **3, 5 und 10 Agenten** durchgeführt werden. Neben den in der Aufgabenstellung geforderten KPIs können dabei weitere Kennzahlen erhoben werden, um Zusammenhänge zwischen der Anzahl der Agenten und der Leistungsfähigkeit des Gesamtsystems zu untersuchen.

### Ausschreibungen ohne Gebot

Jede Ausschreibung besitzt eine Deadline. Gibt innerhalb dieser Frist kein Agent ein Gebot ab, wird der Auftrag verworfen. Dieser Fall wird als eigene KPI erfasst.

Eine mögliche Kennzahl ist die **Quote nicht vergebener Aufträge**:

$$
q_{\text{nicht vergeben}}
=
\frac{\text{Ausschreibungen ohne Gebot}}
{\text{erzeugte Aufträge}}
\cdot 100
$$

Diese Kennzahl kann mit der Anzahl der eingesetzten Agenten korreliert werden. Erwartung: Mit steigender Agentenzahl stehen mehr potenzielle Bieter zur Verfügung und die Anzahl der Ausschreibungen ohne Gebot sollte tendenziell sinken.

### Interessante Zusammenhänge

Besonders interessant erscheint die Untersuchung der folgenden Wirkungskette:

**Agentenzahl → durchschnittliche Anzahl Bieter → Anteil verworfener Aufträge**

Mehr Agenten müssen jedoch nicht ausschließlich positive Auswirkungen haben. Eine größere Anzahl gleichzeitig aktiver Agenten kann zu mehr Bewegungskonflikten und damit zu zusätzlichen A*-Neuplanungen führen.

Damit ergibt sich möglicherweise ein Trade-off:

**Mehr Agenten**

* mehr potenzielle Bieter
* weniger verworfene Aufträge
* möglicherweise kürzere Lieferzeiten
* gleichzeitig möglicherweise mehr Bewegungskonflikte
* dadurch eventuell mehr notwendige Neuplanungen

Es soll daher untersucht werden, ob eine höhere Agentenzahl die Leistungsfähigkeit des Systems kontinuierlich verbessert oder ob ab einer bestimmten Anzahl die zusätzlichen Konflikte einen Teil des Vorteils wieder aufheben.

### Mögliche Visualisierungen mit Seaborn

Für die spätere Auswertung bieten sich unter anderem folgende Darstellungen an:

* Barplot: Agentenanzahl → Anteil verworfener Aufträge
* Barplot: Agentenanzahl → durchschnittliche Anzahl Bieter pro Ausschreibung
* Boxplot: Agentenanzahl → Lieferzeit
* Boxplot: Agentenanzahl → A*-Planungszeit
* Scatterplot: Anzahl der Bieter → Gebotskosten
* Scatterplot: Agentenanzahl/Auslastung → Anzahl Konflikte bzw. Neuplanungen
* Heatmap: Bewegungswege der Agenten mit Markierung von Konfliktpunkten

### Mehrere Simulationsläufe

Für jede Agentenkonfiguration sollten nach Möglichkeit mehrere Simulationsläufe mit unterschiedlichen Zufalls-Seeds durchgeführt werden, beispielsweise 20 bis 50 Läufe pro Konfiguration.

Dadurch entstehen nicht nur einzelne Messwerte für 3, 5 und 10 Agenten, sondern Verteilungen. Diese können insbesondere mit Boxplots dargestellt und miteinander verglichen werden.

Eine mögliche Struktur der gesammelten Daten könnte sein:

```text
run | agents | tasks | awarded | rejected | avg_bidders | collisions | replans
1   | 3      | 50    | 36      | 14       | 1.2         | 3          | 5
2   | 3      | 50    | 39      | 11       | 1.4         | 4          | 7
...
20  | 10     | 50    | 49      | 1        | 4.8         | 21         | 30
```

### Ziel der Auswertung

Die Simulation soll damit nicht nur zeigen, **dass** die Agenten Aufträge verteilen und ausführen können. Sie soll auch sichtbar machen, wie sich die Konfiguration des Multi-Agenten-Systems auf dessen Verhalten auswirkt.

Besonders interessant ist die Frage, ob sich ein Bereich erkennen lässt, in dem zusätzliche Agenten kaum noch einen Vorteil bei der Auftragsvergabe bringen, gleichzeitig aber die Anzahl der Bewegungskonflikte und Neuplanungen zunimmt.


# todos
## better architecture
ANNOUNCE
    -> Agent calculates or requests a complete route
    -> Agent stores the route, for example:
       [(3, 2), (4, 2), (5, 2), ...]
    -> Agent calculates cost
    -> Agent submits BID

Each simulation tick
    -> simulation_engine.py asks the agent for its next position
    -> Agent returns the next route position
    -> simulation_engine.py validates collisions and applies movement

## Agenten und stranded: 
An jedem Depot werden die Agenten komplett geladen. Kostet einen Tick. Somit sollten diese nicht out of Battery laufen  
(wenn sie  immer gut rechnen). Kann kein Auftrag mehr angenommen werden, weil alle Ziele vom aktuellen Standort mit der restlichen Kapazität zu weit weg sind, muss der Agent zum nächsten Depot. Wenn das nicht  geht, oder aber die Agenten aus irgendwelchen Gründen leerlaufen, sind sie "stranded" und werden wie ein Hindernis behandelt.  


Dieses Verhalten muss auf jeden Fall mit in die Dokumentation 

## Agenten und Lieferungen: 
Wenn ein Agent eine Lieferung liefert, muss er die Status setzen:
- Pick up, bei Aufnahme im Depot
- In Transit bei Lieferung
- Delivered bei Abgabe im Depot.

- Diese Angaben müssen als Status - Anzeige in die Depot - Auftrags - Übersicht
- Ebenfalls in die KPIs für Deliveries

## Agenten und Zuschlöge:  
- gewinnt ein Agent, muss das als KPI festgehalten werden
- verliert ein Agent, muss das als KPI festehalten werden 

## KPI Recorder
Eine Zentriere Instanz  
A good migration path is:

Keep the current _store_*_kpi() methods in simulation_engine.py.
Introduce a KpiWriter class later.
Move the CSV-writing code from the engine into KpiWriter.
Let the engine delegate:  

- self.kpi_writer.record_bid_result(event)
- self.kpi_writer.record_package_creation(tick, depot_id, task_id)
- self.kpi_writer.record_simulation(snapshot)

This also allows all existing KPI files to use one component:  
SimulationEngine
    -> KpiWriter
        -> bidding.csv
        -> package_creation.csv
        -> simulation.csv
That is a safe refactoring because:  
Agent remains independent of file storage.
ContractNetManager remains independent of file storage.
Existing KPI formats can remain unchanged.
You can migrate one KPI type at a time.
Tests can replace KpiWriter with an in-memory fake.
So yes, postponing the extraction is reasonable. The current engine is acting as both simulation coordinator and KPI writer, but that can be separated later without redesigning AgentDelivery.  



### nächste Schritte: 
- [x] Agent muss die Status der Lieferungen setzen, die er Ausliefert 
- [x] Ein Gewonnener Aufrag muss den Status: Await Pickup, durch den Agenten steuert werden
- [x] Ein verlorener Aufrag muss als KPI gespeichert werden und dann aus der Liste des Agenten gelöscht werden. 
- [x] Ein gelieferter Auftrag muss der Agenten Liste gelöscht werden. 
- [x] Manhatten Distan z Berechnung ! 


### nächste Schritte am 21.09.2026
- Separater Auction Manager
- Saubere Anzeige der ui. 
- Loggen aller Anzeig in der UI in einer eigenen Log Datei
- Das Loggen muss mit in die Architektur, in dem Passus : Trennung von UI und Simulation. 

- Das alles muss sauber in der UI zu sehen sein. 



 # Refactoring
 - Engine darf keine Logik enthalten.  
   Sie kümmert sich nur um die Konfiguration, intialitiert die UI, startet die Simualation, steuert die UI. 
   Die Simulation , mit allen Logs muss auch ohne UI laufen. !!!!!!