## Aufgabe 1

### Besonderheiten der eigenen Karte

Die Simulation erzeugt bei jedem Start eine neue zufällige Karte mit einer Größe von
15 × 15 Feldern. Dadurch unterscheidet sich die Kartenstruktur bei jedem
Simulationslauf.

Die Karte enthält:

- zufällig platzierte Wandsegmente
- zwei Depots
- vier Lieferziele
- befahrbare Straßenfelder
- eine garantierte Verbindung zwischen allen befahrbaren Bereichen

Beim Erzeugen der Karte wird überprüft, ob alle befahrbaren Felder weiterhin
zusammenhängend erreichbar sind. Ungültige Wandplatzierungen werden verworfen.
Dadurch bleibt die Karte trotz ihrer zufälligen Struktur spielbar.

Eine weitere Besonderheit ist die funktionale Bedeutung der Sonderfelder:

- Steht ein Agent auf einem Depot, führt er die Aktion „Paket aufnehmen“ aus.
- Steht ein Agent auf einem Lieferziel, führt er die Aktion „Paket abliefern“ aus.
- Auf normalen Straßenfeldern kann der Agent zufällig zwischen Bewegung und
  Nachrichtensendung wählen.

Depots und Lieferziele sind dadurch nicht nur optische Markierungen auf der Karte,
sondern bilden aktive Aktionspunkte innerhalb der Simulation. Die Karte beeinflusst
somit direkt das Verhalten der Agenten.

Mit `"random_seed": null` wird bei jedem Start eine neue Karte erzeugt. Aktuell wird
bewusst nur der Wert `null` unterstützt. Die Verwendung eines festen Zufallswerts zur
reproduzierbaren Kartenerzeugung ist derzeit nicht vorgesehen, da dies die
Konfiguration und Logik unnötig komplexer machen würde.

Die Kartenstruktur ist daher bei jedem Start zufällig, während
die grundlegenden Eigenschaften wie Größe, Wanddichte, Anzahl der Depots und Anzahl
der Ziele über die Konfiguration festgelegt bleiben.


### Hauptschleife und zufällige Bewegung

Die Simulation wird tickbasiert ausgeführt. Bei jedem Simulationsschritt wird die
Reihenfolge der Agenten zufällig bestimmt. Anschließend versucht jeder Agent, sich
zufällig auf ein benachbartes befahrbares Feld zu bewegen.

Dabei wird die konfigurierte Geschwindigkeit berücksichtigt. Ein Standard-Agent kann
sich maximal ein Feld pro Tick bewegen, während ein Express-Agent maximal zwei Felder
pro Tick zurücklegt. Nach jedem einzelnen Schritt werden die möglichen Nachbarfelder
neu ermittelt. Wände, bereits belegte Felder und im aktuellen Tick reservierte Felder
werden ausgeschlossen. Dadurch können zwei Agenten nicht gleichzeitig dasselbe Feld
belegen.

Wenn kein gültiges Nachbarfeld verfügbar ist, beendet der Agent seine Bewegung für
diesen Tick. Eine echte Wegplanung oder die Suche nach einem längeren Umweg findet in
diesem Meilenstein noch nicht statt. Die Agentenbewegung ist bewusst zufällig und dient
als Vorbereitung für die spätere A*-Wegsuche in Meilenstein 3.

Die Kommunikation zwischen Agenten, das Aufnehmen und Abliefern von Paketen sowie die
Planung konkreter Aktionen werden in den folgenden Aufgaben ergänzt.  Die aktuelle
Hauptschleife protokolliert bereits den Simulationsfortschritt und zeigt die Agenten,
Tasks und Nachrichten in der Benutzeroberfläche an.


## Aufgabe 2
Für die Aufgabe 2 starte ich mit der Implementierung der Pakete in den Depots. 
Das ist, auf den ersten Blick der leichteste Schritt und sollte nur lose an den Rest des
Protokolls und der Vergabelogik gebunden sein. 

Das Protkoll:  
# Contract Net Protocol (CNP) – angepasst auf meine Paketzustellungssimulation

## Grundidee

Das **Contract Net Protocol (CNP)** ist ein Protokoll zur Aufgabenverteilung in einem Multi-Agenten-System.

In meiner Simulation werden Pakete in unterschiedlichen Depots erzeugt. Ein zentraler **ContractNetManager** übernimmt anschließend die komplette Vergabe des Lieferauftrags.

Die Lieferagenten erhalten die Ausschreibung, prüfen selbstständig, ob sie den Auftrag übernehmen können, berechnen ihre Kosten und geben gegebenenfalls ein Angebot ab.

Der Manager sammelt die Angebote und vergibt den Auftrag an den günstigsten Agenten.

---

## Rollen in der Simulation

### Depot

Ein Depot erzeugt ein neues Paket.

Die Depots übernehmen **nicht** die Vergabe des Pakets.

Ihre Aufgabe ist lediglich:

```text
Paket erzeugen
    ↓
Manager informieren
```

Welches Depot ein Paket erzeugt, wird zufällig bestimmt.

---

### ContractNetManager

Der `ContractNetManager` übernimmt die Manager-Rolle des Contract Net Protocols.

Seine Aufgaben sind:

1. Neue Pakete entgegennehmen
2. Ausschreibung an die Agenten senden
3. Angebote sammeln
4. Angebote vergleichen
5. Gewinner bestimmen
6. Zuschlag erteilen

Der Manager berechnet dabei **nicht selbst**, welcher Agent den Auftrag am besten erfüllen kann.

Diese Bewertung erfolgt zunächst durch die einzelnen Agenten.

---

### Lieferagenten

Die Lieferagenten sind die sogenannten **Contractors**.

Jeder Agent besitzt einen eigenen Zustand, beispielsweise:

* Position
* Kapazität
* Batteriestand
* Agententyp
* aktuelle Aufträge

Nach einer Ausschreibung entscheidet jeder Agent selbst:

```text
Kann ich diesen Auftrag übernehmen?
```

Falls ja, berechnet er seine Kosten und sendet ein Angebot an den Manager.

Falls nein, gibt er kein Angebot ab.

---

# Ablauf des Contract Net Protocols

## 1. Paket wird erzeugt

Alle fünf Simulationsschritte wird an einem zufällig ausgewählten Depot ein neues Paket erzeugt.

Beispiel:

```text
Simulation Step 35

Depot 2 erzeugt:

Task-ID:     184
Ziel:        Z3
Deadline:    120
```

Das Depot informiert anschließend den `ContractNetManager`.

Dieses Ereignis kann beispielsweise intern als

```text
PackageCreated
```

bezeichnet werden.

`PackageCreated` ist keine eigentliche CNP-Nachricht, sondern löst das Bieterverfahren aus.

---

# 2. ANNOUNCE – Ausschreibung

Der Manager erstellt nun eine Ausschreibung für den Auftrag.

Die Nachricht lautet:

```text
ANNOUNCE(
    task_id,
    destination,
    deadline
)
```

Beispiel:

```text
ANNOUNCE(
    task_id = 184,
    destination = Z3,
    deadline = 120
)
```

Diese Nachricht wird an alle relevanten Lieferagenten gesendet.

Der Manager sagt damit sinngemäß:

> Es gibt einen neuen Lieferauftrag. Wer kann ihn übernehmen und zu welchen Kosten?

---

# 3. Agent bewertet den Auftrag

Jeder Agent erhält dieselbe Ausschreibung.

Danach führt jeder Agent selbstständig seine eigene Bewertung durch.

Der Ablauf sieht beispielsweise so aus:

```text
ANNOUNCE erhalten
        ↓
Kann ich den Auftrag übernehmen?
        ↓
   ┌────┴────┐
   │         │
  Nein       Ja
   │         │
kein BID     ↓
        Kosten berechnen
             ↓
          BID senden
```

Ein Agent könnte beispielsweise feststellen:

```text
Agent 1
Position: (2,3)
Auftrag möglich
Kosten: 18
```

Ein anderer Agent:

```text
Agent 2
Batteriestand zu niedrig
Auftrag nicht möglich
kein Gebot
```

Ein dritter Agent:

```text
Agent 3
Position: (8,7)
Auftrag möglich
Kosten: 12
```

---

# 4. BID – Angebot

Kann ein Agent den Auftrag übernehmen, sendet er ein Angebot an den Manager.

Die Nachricht lautet:

```text
BID(
    agent_id,
    task_id,
    cost
)
```

Beispiel:

```text
BID(
    agent_id = 3,
    task_id = 184,
    cost = 12
)
```

Der Manager könnte anschließend folgende Angebote besitzen:

| Agent   | Kann liefern | Kosten |
| ------- | ------------ | -----: |
| Agent 1 | Ja           |     18 |
| Agent 2 | Nein         |      - |
| Agent 3 | Ja           |     12 |
| Agent 4 | Ja           |     21 |

Agent 2 gibt kein Gebot ab.

---

# 5. Angebote sammeln

Der Manager sammelt die `BID`-Nachrichten.

Dabei berechnet der Manager die Kosten nicht selbst.

Er kennt lediglich die Angebote der Agenten.

```text
Agent 1 → BID 18

Agent 3 → BID 12

Agent 4 → BID 21
```

Damit bleibt die Bewertung des Auftrags dezentral bei den Agenten.

---

# 6. Angebote bewerten

Wenn der Manager entsprechend der Simulationslogik wieder an der Reihe ist, wertet er die vorhandenen Angebote aus.

In meiner Simulation lautet die Vergaberegel:

> Der Agent mit den niedrigsten Kosten gewinnt.

Damit ergibt sich:

```text
Agent 1 → 18

Agent 3 → 12   ← Gewinner

Agent 4 → 21
```

Der Gewinner ist somit:

```text
Agent 3
```

---

# 7. AWARD – Zuschlag

Der Manager erteilt dem Gewinner den Zuschlag.

Die Nachricht lautet:

```text
AWARD(
    task_id,
    agent
)
```

Beispiel:

```text
AWARD(
    task_id = 184,
    agent = Agent3
)
```

Damit erhält Agent 3 offiziell den Lieferauftrag.

---

# Gesamter Ablauf

```text
Depot
  │
  │ PackageCreated
  ▼
ContractNetManager
  │
  │ ANNOUNCE
  ▼
┌───────────────────────────┐
│       Lieferagenten       │
│                           │
│ Agent 1 → BID 18          │
│ Agent 2 → kein BID        │
│ Agent 3 → BID 12          │
│ Agent 4 → BID 21          │
└────────────┬──────────────┘
             │
             │ BID
             ▼
      ContractNetManager
             │
             │ Angebote vergleichen
             │
             ▼
        Agent 3 gewinnt
             │
             │ AWARD
             ▼
          Agent 3
```

---

# Nachrichten des Protokolls

In der Simulation werden drei Nachrichtenarten verwendet:

## ANNOUNCE

Sender:

```text
ContractNetManager
```

Empfänger:

```text
Lieferagenten
```

Bedeutung:

```text
Es gibt einen neuen Auftrag.
Wer möchte ihn übernehmen?
```

Struktur:

```text
ANNOUNCE(task_id, destination, deadline)
```

---

## BID

Sender:

```text
Lieferagent
```

Empfänger:

```text
ContractNetManager
```

Bedeutung:

```text
Ich kann den Auftrag übernehmen.
Meine Kosten betragen X.
```

Struktur:

```text
BID(agent_id, task_id, cost)
```

---

## AWARD

Sender:

```text
ContractNetManager
```

Empfänger:

```text
Gewinner der Ausschreibung
```

Bedeutung:

```text
Du erhältst den Auftrag.
```

Struktur:

```text
AWARD(task_id, agent)
```

---

# Verantwortlichkeiten

Die Verantwortlichkeiten sind klar getrennt:

```text
DEPOT

erzeugt Paket
      ↓

MANAGER

organisiert Ausschreibung
      ↓

AGENTEN

bewerten Auftrag
und berechnen Kosten
      ↓

MANAGER

vergleicht Angebote
und vergibt Auftrag
      ↓

GEWINNER

übernimmt Auftrag
```

---

# Was ist daran das Contract Net Protocol?

Der zentrale Punkt ist die Trennung zwischen **Ausschreibung**, **Bewertung** und **Vergabe**.

Der Manager sagt nicht:

```text
Agent 3 muss Paket 184 liefern.
```

Stattdessen sagt er:

```text
Wer kann Paket 184 liefern?
```

Die Agenten treffen daraufhin selbst eine Entscheidung.

```text
Agent 1:
Ich kann liefern.
Kosten: 18

Agent 2:
Ich kann nicht liefern.

Agent 3:
Ich kann liefern.
Kosten: 12
```

Erst danach entscheidet der Manager:

```text
Agent 3 bekommt den Auftrag.
```

Damit ist die Entscheidung teilweise dezentralisiert:

* Der **Agent** entscheidet, ob und zu welchen Kosten er bietet.
* Der **Manager** entscheidet, welches Angebot gewinnt.

---

# Kurzfassung

Das Contract Net Protocol meiner Simulation lässt sich auf folgenden Ablauf reduzieren:

```text
1. Paket entsteht

2. Manager schreibt Auftrag aus
   ANNOUNCE

3. Agenten prüfen den Auftrag

4. geeignete Agenten berechnen ihre Kosten

5. Agenten senden ihre Angebote
   BID

6. Manager sammelt die Angebote

7. Manager bestimmt den günstigsten Anbieter

8. Gewinner erhält den Zuschlag
   AWARD
```

Die Kernidee lautet:

> **Der Manager verteilt den Auftrag nicht direkt, sondern schreibt ihn aus. Die Agenten bewerten den Auftrag selbst und konkurrieren mit ihren Angeboten um den Zuschlag.**


