##Aufgabe 1

### Besonderheiten der eigenen Karte

Die Simulation erzeugt bei jedem Start eine neue zufällige Karte mit einer Größe von
15 × 15 Feldern. Dadurch unterscheidet sich die Kartenstruktur bei jedem Simulationslauf.

Die Karte enthält:

- zufällig platzierte Wandsegmente
- zwei Depots
- vier Lieferziele
- befahrbare Straßenfelder
- eine garantierte Verbindung zwischen allen befahrbaren Bereichen

Beim Erzeugen wird überprüft, ob die Karte weiterhin zusammenhängend und damit vollständig
befahrbar bleibt. Ungültige Wandplatzierungen werden verworfen.

Die Karte ist dadurch zufällig und abwechslungsreich, bleibt aber trotzdem spielbar. Die
Anzahl der Depots und Ziele sowie die maximale Wanddichte werden über die Konfiguration
festgelegt. Mit `random_seed: null` entsteht bei jedem Start eine neue Karte.  

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
