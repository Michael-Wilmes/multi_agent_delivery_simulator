##Aufgabe 1

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
Planung konkreter Aktionen werden in den folgenden Meilensteinen ergänzt. Die aktuelle
Hauptschleife protokolliert bereits den Simulationsfortschritt und zeigt die Agenten,
Tasks und Nachrichten in der Benutzeroberfläche an.
