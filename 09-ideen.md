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
