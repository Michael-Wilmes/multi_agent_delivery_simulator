## Architektur

Die Architektur der Simulation folgt den Grundprinzipien **Keep it Simple (KISS)** und **Separation of Concerns**. Die einzelnen Komponenten besitzen klar abgegrenzte Verantwortlichkeiten und sollen nur das Wissen enthalten, das sie zur Erfüllung ihrer jeweiligen Aufgabe benötigen.

Dadurch soll die Komplexität des Gesamtsystems begrenzt und gleichzeitig ermöglicht werden, einzelne Komponenten gezielt zu verändern oder zu erweitern, ohne größere Änderungen an anderen Teilen des Systems vornehmen zu müssen.

### Trennung von Benutzeroberfläche und Simulationslogik

Eine grundlegende Architekturentscheidung ist die vollständige Trennung der eigentlichen Simulationslogik von der Benutzeroberfläche.

Die Simulation benötigt keine grafische Benutzeroberfläche für ihre Ausführung. Sämtliche für die Simulation notwendigen Komponenten, Zustände und Abläufe befinden sich im Simulationskern. Die Benutzeroberfläche dient ausschließlich der Darstellung des aktuellen Simulationszustands sowie der Interaktion mit der Simulation.

Dadurch kann die Simulation vollständig **headless**, also ohne grafische Benutzeroberfläche, ausgeführt werden.

Die grundlegende Struktur lässt sich vereinfacht wie folgt darstellen:

```text id="wcdsyc"
                     +----------------+
                     |   Desktop UI   |
                     +-------+--------+
                             |
                             |
+----------------------------+----------------------------+
|                    Simulation Core                      |
|                                                         |
|   Depots                 ContractNetManager              |
|                                |                        |
|                         AuctionManager                  |
|                                                         |
|   Agents                    RouteManager                 |
|                                                         |
|                     Simulation Clock                    |
+---------------------------------------------------------+
```

Die Benutzeroberfläche stellt damit lediglich eine mögliche Präsentationsschicht des Simulationssystems dar.

Diese Trennung ermöglicht insbesondere die spätere Verwendung alternativer Benutzeroberflächen. Beispielsweise könnte die bestehende Oberfläche durch ein webbasiertes Frontend ersetzt oder um ein solches ergänzt werden, ohne die eigentliche Simulationslogik verändern zu müssen.

Konzeptionell sind daher unterschiedliche Betriebs- und Darstellungsformen möglich:

```text id="1fq18m"
                     +-- Desktop UI
                     |
Simulation Core -----+-- Web UI
                     |
                     +-- CLI
                     |
                     +-- Headless / Batch
```

Der Headless-Betrieb besitzt zusätzlich einen wichtigen Vorteil für die experimentelle Nutzung der Simulation. Simulationsreihen können automatisiert und ohne den zusätzlichen Aufwand einer grafischen Darstellung durchgeführt werden.

So können beispielsweise unterschiedliche Systemkonfigurationen mehrfach ausgeführt und die dabei erhobenen Kennzahlen anschließend miteinander verglichen werden.

Die Benutzeroberfläche ist somit **Konsument des Simulationszustands, aber keine Voraussetzung für die Funktionsfähigkeit der Simulation**.

### Grundlegende Komponenten des Simulationskerns

Der Simulationskern besteht im Wesentlichen aus folgenden Komponenten:

* **Agenten** repräsentieren die autonomen Teilnehmer des Systems.
* **Depots** erzeugen und verwalten Transportaufträge.
* Der **ContractNetManager** bildet die zentrale Kommunikations- und Vermittlungskomponente des Contract-Net-Verfahrens.
* Der **AuctionManager** verwaltet Ausschreibungen, Gebote, Deadlines und die eigentliche Vergabe der Aufträge.
* Der **RouteManager** übernimmt die zentrale Wegplanung und Kollisionsvermeidung.
* Die **Simulation Clock** stellt den gemeinsamen zeitlichen Ablauf der diskreten Simulation über Simulationsticks sicher.

Die Verantwortlichkeiten dieser Komponenten werden bewusst voneinander getrennt.

### Autonomie der Agenten

Die Agenten handeln innerhalb ihres jeweiligen Verantwortungsbereichs autonom. Autonomie bedeutet dabei nicht, dass jeder Agent sämtliche Entscheidungen des Gesamtsystems selbst treffen muss.

Wird ein neuer Auftrag ausgeschrieben, entscheidet ein Agent eigenständig, ob er an der Ausschreibung teilnimmt und ein Gebot abgibt. Grundlage hierfür sind sein eigener Zustand und seine aktuelle Auftragsplanung.

Globale Koordinationsaufgaben werden dagegen bewusst an spezialisierte Komponenten delegiert. Dadurch müssen die Agenten beispielsweise weder die Auftragsvergabe untereinander aushandeln noch globale Informationen über die geplanten Bewegungen anderer Agenten verwalten.

Die Architektur kann daher als **Multiagentensystem mit zentralen Koordinationsdiensten** betrachtet werden.

### Kommunikation über den ContractNetManager

Der `ContractNetManager` bildet den zentralen Kommunikationsweg für die auftragsbezogene Kommunikation innerhalb des Multiagentensystems.

Agenten registrieren sich beim `ContractNetManager` und kommunizieren bezüglich Ausschreibungen, Geboten und Zustandsänderungen von Aufträgen ausschließlich über diese Komponente.

Der `ContractNetManager` übernimmt jedoch bewusst **nicht die fachliche Durchführung einer Auktion**.

Seine Aufgabe besteht darin, Nachrichten zwischen den beteiligten Komponenten zu vermitteln und die Schnittstelle zwischen Depots, Agenten und dem `AuctionManager` bereitzustellen.

Vereinfacht ergibt sich folgende Kommunikationsstruktur:

```text id="y50ek4"
                     Depot
                       |
                       v
              ContractNetManager
                 /           \
                /             \
               v               v
       AuctionManager        Agents
```

Der `AuctionManager` benötigt dadurch keinen eigenen Kommunikationsmechanismus zu den Agenten.

Diese Trennung verhindert, dass Kommunikationslogik und Vergabelogik miteinander vermischt werden.

### AuctionManager

Der `AuctionManager` ist vollständig für den Lebenszyklus einer Ausschreibung verantwortlich.

Wird durch ein Depot ein neuer Auftrag erzeugt, gelangt dieser zunächst zum `ContractNetManager`. Dieser übergibt den Auftrag an den `AuctionManager`, der daraus eine neue Ausschreibung erzeugt.

Zu seinen Aufgaben gehören insbesondere:

* Erzeugen und Verwalten einer Ausschreibung,
* Festlegen bzw. Verwalten der zugehörigen Deadline,
* Sammeln und Zuordnen eingehender Gebote,
* Beenden der Ausschreibung nach Ablauf der Deadline,
* Bewerten der eingegangenen Gebote,
* Ermitteln des erfolgreichen Gebots,
* Bereitstellen des Ergebnisses der Ausschreibung.

Der `AuctionManager` ist damit für die Frage verantwortlich:

> **Welches Gebot gewinnt die Ausschreibung?**

Er ist dagegen nicht dafür verantwortlich, die hierfür notwendigen Nachrichten selbst an Agenten zu übertragen.

### Auftragsvergabe mittels Contract Net

Die Auftragsvergabe orientiert sich am Contract Net Protocol.

Ein Depot erzeugt zunächst einen neuen Transportauftrag und übergibt diesen an den `ContractNetManager`.

Der `ContractNetManager` übergibt den Auftrag an den `AuctionManager`. Dieser erzeugt und verwaltet die zugehörige Ausschreibung.

Die Veröffentlichung gegenüber den registrierten Agenten erfolgt anschließend über den `ContractNetManager` mittels einer `ANNOUNCE`-Nachricht.

```text id="mds9bw"
Depot
  |
  | neuer Auftrag
  v
ContractNetManager
  |
  | Auftrag
  v
AuctionManager
  |
  | Ausschreibung erzeugen
  |
  v
ContractNetManager
  |
  | ANNOUNCE
  +--------------------------+
  |                          |
  v                          v
Agent A                    Agent B
```

Jeder Agent entscheidet anschließend selbstständig, ob er an der Ausschreibung teilnehmen möchte.

Entscheidet er sich für eine Teilnahme, berechnet er die Kosten für die Übernahme des Auftrags und sendet ein `BID` an den `ContractNetManager`.

Dieser leitet das Gebot an den `AuctionManager` weiter:

```text id="grg3fn"
Agent
  |
  | BID
  v
ContractNetManager
  |
  | BID
  v
AuctionManager
```

Der `AuctionManager` sammelt die eingegangenen Gebote bis zum Erreichen der Deadline.

Nach Ablauf der Deadline wird die Ausschreibung geschlossen und die eingegangenen Gebote werden bewertet. Der `AuctionManager` bestimmt anschließend das erfolgreiche Gebot und stellt das Ergebnis dem `ContractNetManager` zur Verfügung.

Dieser übernimmt wiederum die Kommunikation mit den Agenten:

```text id="k6xtef"
                    AuctionManager
                          |
                          | Ergebnis
                          v
                  ContractNetManager
                    /           \
                   /             \
                 WIN          BID_LOST
                  |               |
                  v               v
              Gewinner        übrige Bieter
```

Damit besteht eine klare Trennung zwischen **Vergabeentscheidung und Kommunikation**:

```text id="pjmvw7"
AuctionManager
    |
    +-- Was wird ausgeschrieben?
    +-- Welche Gebote liegen vor?
    +-- Wann endet die Auktion?
    +-- Welches Gebot gewinnt?


ContractNetManager
    |
    +-- Wer erhält ANNOUNCE?
    +-- Weiterleitung der BIDs
    +-- Übermittlung von WIN
    +-- Übermittlung von BID_LOST
    +-- Vermittlung weiterer Task-Nachrichten
```

### Lebenszyklus eines Auftrags

Nach erfolgreicher Vergabe erhält der Auftrag im Depot den Status `await_pickup`.

Der erfolgreiche Agent fährt anschließend zum entsprechenden Depot. Der Ladevorgang benötigt einen Simulationstick. Nach dem Pickup wechselt der Auftrag im Depot in den Zustand `in_transport`.

Nach Erreichen des Zielortes meldet der Agent die erfolgreiche Auslieferung. Der Auftrag wird aus der Auftragsliste des Agenten entfernt und erhält im Depot den Status `delivered`.

Der vereinfachte Lebenszyklus lautet:

```text id="sk8dbf"
Auftrag erzeugt
      |
      v
Ausschreibung
      |
      v
Vergabe
      |
      v
await_pickup
      |
      | Agent erreicht Depot
      | + 1 Tick Ladezeit
      v
in_transport
      |
      | Agent erreicht Ziel
      v
delivered
```

Auch nach Abschluss der Auktion laufen auftragsbezogene Nachrichten weiterhin über den `ContractNetManager`.

Der `AuctionManager` ist an der eigentlichen Ausführung eines bereits vergebenen Auftrags nicht mehr beteiligt.

Dadurch endet seine Verantwortung mit der abgeschlossenen Vergabe.

### Verzicht auf direkte Inter-Agenten-Kommunikation

Eine direkte Kommunikation zwischen den Agenten wurde bewusst nicht vorgesehen.

Die für die Simulation notwendige Koordination erfolgt bereits über den `ContractNetManager`, den `AuctionManager` und den `RouteManager`.

Eine zusätzliche direkte Kommunikation zwischen Agenten würde weitere Koordinationsmechanismen erforderlich machen, ohne für das betrachtete Szenario einen notwendigen funktionalen Mehrwert zu liefern.

Insbesondere müssten bei konkurrierenden Interessen zusätzliche Regeln definiert werden. Möchten beispielsweise zwei Agenten zum gleichen Zeitpunkt dieselbe Position belegen, müsste bei direkter Kommunikation festgelegt werden, welcher Agent Priorität besitzt.

Daraus würden zusätzliche Fragestellungen hinsichtlich Priorisierung, gleichzeitig eintreffender Nachrichten, Deadlocks und möglicher Wartezustände entstehen.

Auf diese zusätzliche Komplexität wird bewusst verzichtet.

Sollte eine spätere Erweiterung eine tatsächliche Kooperation oder Verhandlung zwischen Agenten erfordern, kann eine entsprechende Kommunikationsform gezielt ergänzt werden.

### Zentrale Routenplanung

Die Wegplanung wird bewusst aus den Agenten ausgelagert und durch einen zentralen `RouteManager` durchgeführt.

Ein Agent übermittelt dem `RouteManager` die für eine Wegberechnung notwendigen Informationen, insbesondere Startposition, Zielposition und den vorgesehenen Startzeitpunkt.

Der `RouteManager` berechnet daraufhin eine geeignete Route.

Da der `RouteManager` die bereits geplanten Routen kennt, kann er bei der Berechnung bestehende Reservierungen berücksichtigen und dadurch Kollisionen zwischen geplanten Bewegungen vermeiden.

Eine Route wird dabei nicht ausschließlich räumlich betrachtet. Da eine Kollision nur dann entsteht, wenn zwei Bewegungen dieselbe Position zum gleichen Zeitpunkt beanspruchen, besitzt die Planung zusätzlich eine zeitliche Dimension.

Ein Routenschritt kann somit vereinfacht als

$$
(x, y, t)
$$

betrachtet werden, wobei \(x\) und \(y\) die Position und \(t\) den entsprechenden Simulationstick repräsentieren.

Auch das Warten an einer Position kann dadurch als gültiger Routenschritt modelliert werden:

```text id="qz8fkd"
Tick 10     (4,5)
Tick 11     (4,5)    <- WAIT
Tick 12     (4,6)
Tick 13     (4,7)
```

Dadurch muss bei einer zeitlichen Überschneidung nicht zwangsläufig eine vollständig andere räumliche Route gewählt werden.

### Entkopplung des RouteManagers von den Agenten

Der `RouteManager` soll bewusst keine Kenntnis darüber besitzen, welcher Agent eine bestimmte Route verwendet.

Für die Kollisionsvermeidung ist die Identität eines Agenten nicht relevant. Entscheidend ist ausschließlich, ob eine bestimmte Position zu einem bestimmten Zeitpunkt bereits reserviert ist.

Der `RouteManager` verwaltet daher **Routenreservierungen und keine Agenten**.

Eine Anfrage kann beispielsweise zu folgendem Ergebnis führen:

```text id="8mzw68"
RouteRequest
     |
     v
RouteManager
     |
     v
RouteReservation
     |
     +-- ReservationId
     |
     +-- Route
          |
          +-- (x, y, t)
          +-- (x, y, t+1)
          +-- (x, y, t+2)
          +-- ...
```

Die Zuordnung zwischen Agent und Route bleibt außerhalb des `RouteManager`.

Über eine `ReservationId` kann eine bestehende Reservierung eindeutig referenziert und bei Bedarf wieder aufgehoben oder ersetzt werden. Der `RouteManager` benötigt dafür keine `AgentId`.

Seine zentrale Fragestellung lautet damit nicht:

> „Wo befindet sich Agent X?“

sondern:

> „Ist Position `(x,y)` zum Zeitpunkt `t` bereits reserviert?“

Diese Entkopplung ermöglicht es außerdem, die Routenplanung unabhängig vom restlichen Agentensystem zu entwickeln und zu testen.

### Trennung der Verantwortlichkeiten

Aus den beschriebenen Entscheidungen ergibt sich folgende grundlegende Aufteilung:

```text id="l4epjh"
Simulation Core
|
+-- Depot
|    |
|    +-- Erzeugung von Aufträgen
|    +-- Verwaltung des Task-Zustands
|
+-- ContractNetManager
|    |
|    +-- Registrierung der Agenten
|    +-- zentrale Nachrichtenvermittlung
|    +-- ANNOUNCE
|    +-- Weiterleitung von BID
|    +-- Übermittlung von WIN / BID_LOST
|    +-- Vermittlung weiterer Task-Nachrichten
|
+-- AuctionManager
|    |
|    +-- Verwaltung der Ausschreibungen
|    +-- Verwaltung der Deadlines
|    +-- Sammlung der Gebote
|    +-- Bewertung der Gebote
|    +-- Ermittlung des Gewinners
|
+-- Agent
|    |
|    +-- eigener Zustand
|    +-- eigene Auftragsliste
|    +-- Entscheidung über Teilnahme an Ausschreibungen
|    +-- Berechnung des Gebots
|    +-- Ausführung angenommener Aufträge
|
+-- RouteManager
|    |
|    +-- Wegberechnung
|    +-- Verwaltung von Routenreservierungen
|    +-- zeitliche Planung
|    +-- Kollisionsvermeidung
|
+-- Simulation Clock
     |
     +-- Verwaltung der Simulationsticks
     +-- zeitliche Synchronisation der Simulation
```

Die Verantwortlichkeiten lassen sich damit auf wenige zentrale Fragestellungen reduzieren:

```text id="50u7w2"
Depot
    "Welche Aufträge existieren und welchen Status haben sie?"

Agent
    "Biete ich auf einen Auftrag und wie führe ich ihn aus?"

ContractNetManager
    "Wie werden die beteiligten Komponenten miteinander verbunden?"

AuctionManager
    "Welches Gebot gewinnt die Ausschreibung?"

RouteManager
    "Wie gelangt etwas kollisionsfrei von A nach B?"

Simulation Clock
    "Welcher Simulationszeitpunkt liegt aktuell vor?"
```

### Architekturprinzipien

Die Architektur verfolgt bewusst keine maximale Dezentralisierung. Stattdessen wird für jede Aufgabe entschieden, welche Komponente die dafür notwendigen Informationen besitzt und wo die entsprechende Verantwortung sinnvoll angesiedelt werden kann.

Die wesentlichen Leitgedanken sind:

* **Keep it Simple:** Es werden nur Kommunikations- und Koordinationsmechanismen implementiert, die für das betrachtete Szenario tatsächlich benötigt werden.
* **Separation of Concerns:** Jede Komponente besitzt einen klar abgegrenzten Verantwortungsbereich.
* **Lose Kopplung:** Komponenten besitzen möglichst wenig Wissen über die interne Funktionsweise anderer Komponenten.
* **Gezielte Erweiterbarkeit:** Neue Anforderungen sollen möglichst durch Änderungen oder Ergänzungen einzelner Komponenten umgesetzt werden können.
* **Austauschbarkeit:** Insbesondere Wegplanung, Vergabestrategie und Benutzeroberfläche können unabhängig voneinander verändert oder ersetzt werden.
* **Testbarkeit:** Komponenten wie `AuctionManager` und `RouteManager` können unabhängig vom vollständigen Multiagentensystem getestet werden.
* **UI-Unabhängigkeit:** Die Simulationslogik ist unabhängig von ihrer Darstellung und kann sowohl mit unterschiedlichen Benutzeroberflächen als auch vollständig headless betrieben werden.

Die Aufteilung zwischen `ContractNetManager` und `AuctionManager` folgt diesen Prinzipien besonders deutlich. Der `ContractNetManager` stellt die Kommunikationsstruktur des Contract-Net-Verfahrens bereit, während der `AuctionManager` ausschließlich die fachliche Durchführung und Entscheidung der Ausschreibungen übernimmt.

Dadurch können beispielsweise die Vergabestrategie oder die Regeln einer Ausschreibung verändert werden, ohne die Kommunikationsmechanismen zwischen den Agenten anpassen zu müssen. Umgekehrt können Änderungen an der Nachrichtenvermittlung vorgenommen werden, ohne die eigentliche Vergabelogik zu verändern.

Ziel ist nicht, ein möglichst komplexes oder vollständig dezentrales Multiagentensystem zu entwickeln. Stattdessen soll eine nachvollziehbare und für die Aufgabenstellung angemessene Architektur entstehen, bei der autonome Agenten mit klar abgegrenzten zentralen Koordinationsdiensten zusammenarbeiten und unnötige Abhängigkeiten zwischen den einzelnen Komponenten vermieden werden.
