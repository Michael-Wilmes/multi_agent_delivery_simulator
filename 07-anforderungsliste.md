# Anforderungsliste: Multi-Agenten-Liefersimulation

> **Zweck:** Zentrale, abhakelbare Arbeits-, Abnahme- und Nachweisliste für die Umsetzung mit Python, Pygame, Contract-Net, A\*, Prolog und Auswertung.
>
> **Quellengrundlage:** `Fahrplan_4_Wochen_MAS_Pygame_v2.pdf` und `Fahrplan_4_Wochen_MAS_Pygame.pdf`.
>
> **Wichtiger Hinweis:** Die beiden Fahrpläne verweisen auf ein separates Original-Aufgabenblatt beziehungsweise eine bereits ausgefüllte Aufgabenmatrix. Dieses Original lag bei der Erstellung dieser Datei nicht vor. Punkte mit **[BLATT PRÜFEN]** müssen deshalb zwingend mit dem Original abgeglichen werden. Die Liste enthält alle Anforderungen und konkret genannten Prüfpunkte aus den beiden verfügbaren Fahrplänen, erhebt aber ohne das Originalblatt keinen Anspruch darauf, unbekannte Originalformulierungen abzubilden.

---

## 0. Anforderungsabgleich und Projektsteuerung

- [ ] Original-Aufgabenblatt vollständig beschaffen.
- [ ] Original-Aufgabenblatt Punkt für Punkt mit dieser Liste abgleichen.
- [ ] Jede Originalanforderung als Muss-, Kann- oder Komfortanforderung kennzeichnen.
- [ ] Abweichende oder fehlende Anforderungen ergänzen.
- [ ] Nur als `ABGLEICH` markierte Punkte korrigieren, wenn bereits eine ausgefüllte Matrix existiert.
- [ ] Für jede Muss-Anforderung eine eindeutige Definition of Done formulieren.
- [ ] Für jede Anforderung ein Abnahmekriterium festlegen.
- [ ] Für jede Anforderung einen Nachweis festlegen, zum Beispiel automatisierter Test, Screenshot, Log, CSV oder Dokumentationsstelle.
- [ ] Für jede Anforderung den Umsetzungsstatus pflegen.
- [ ] Für jede Anforderung eine Zielwoche festlegen.
- [ ] Aufgabenmatrix als verbindliches operatives Steuerungsinstrument verwenden.
- [ ] Nach jeder Arbeitssitzung einen Commit erstellen.
- [ ] Nach jeder Arbeitssitzung neue Architekturentscheidungen kurz dokumentieren.
- [ ] Nach jeder Arbeitssitzung genau den nächsten konkreten Schritt festhalten.
- [ ] Bei Zeitdruck zuerst Komfort und Optik reduzieren, nicht Pflichtlogik oder Nachweise.

### Abnahme

- [ ] Keine bekannte Anforderung ist nur implizit vorhanden.
- [ ] Jede Muss-Anforderung ist Code, Test, Screenshot, Log, CSV oder Dokumentation zugeordnet.
- [ ] Aufgabenliste und tatsächlicher Projektstand stimmen überein.

---

## 1. Projektgrundlage und Entwicklungsumgebung

- [ ] Python-Version festlegen und dokumentieren.
- [ ] Virtuelle Python-Umgebung anlegen.
- [ ] Projektabhängigkeiten in einer Abhängigkeitsdatei pflegen.
- [ ] Pygame als Abhängigkeit aufnehmen.
- [ ] Testframework einrichten.
- [ ] Vorhandenen Smoke-Test ausführen.
- [ ] Projektstart auf dem Entwicklungsrechner erfolgreich testen.
- [ ] Saubere Trennung zwischen Fachlogik, Simulation, Darstellung und Integration herstellen.
- [ ] Keine Fachlogik direkt im Pygame-Eventloop implementieren.
- [ ] Keine unnötigen Sprite-Klassen einführen.
- [ ] Keine Animationen, Sounds oder zusätzlichen GUI-Frameworks einführen, sofern nicht ausdrücklich gefordert.
- [ ] Keine Mausbedienung voraussetzen, sofern das Originalblatt sie nicht verlangt. **[BLATT PRÜFEN]**

### Pygame-Grundlagen

- [ ] Pygame initialisieren.
- [ ] Fenster und Zeichenfläche erzeugen.
- [ ] Fenster kontrolliert schließen können.
- [ ] Eventloop implementieren.
- [ ] Tastatureingaben erkennen.
- [ ] Rechtecke zeichnen.
- [ ] Kreise zeichnen.
- [ ] Text rendern.
- [ ] Frames über eine Clock begrenzen.
- [ ] Gezeichneten Frame sichtbar aktualisieren.
- [ ] Simulationstakt und Bildrate voneinander trennen.

### Abnahme

- [ ] Projekt startet ohne ungefangene Ausnahme.
- [ ] Fenster lässt sich regulär schließen.
- [ ] Fachlogik kann ohne geöffnetes Pygame-Fenster getestet werden.

---

## 2. Domänenmodell

- [ ] Klasse beziehungsweise Datentyp `Position` modellieren.
- [ ] Klasse beziehungsweise Datentyp `Zelle` modellieren.
- [ ] Klasse beziehungsweise Datentyp `Auftrag` modellieren.
- [ ] Klasse beziehungsweise Datentyp `AgentState` modellieren.
- [ ] Klasse beziehungsweise Datentyp `Nachricht` modellieren.
- [ ] Karte beziehungsweise Grid als eigenes Modell abbilden.
- [ ] Befahrbare Straße modellieren.
- [ ] Wand beziehungsweise Hindernis modellieren.
- [ ] Depot modellieren.
- [ ] Ziel modellieren.
- [ ] Agent modellieren.
- [ ] Mindestens zwei Agententypen modellieren.
- [ ] Agenten-ID eindeutig machen.
- [ ] Agentengeschwindigkeit modellieren.
- [ ] Agentenstatus modellieren.
- [ ] Aktuelles Agentenziel modellieren.
- [ ] Agentenkapazität modellieren, falls gefordert. **[BLATT PRÜFEN]**
- [ ] Batteriezustand modellieren, falls gefordert. **[BLATT PRÜFEN]**
- [ ] Ladungszustand modellieren, falls gefordert. **[BLATT PRÜFEN]**
- [ ] Auftragsstatus modellieren.
- [ ] Beziehungen zwischen Auftrag, Depot, Ziel und Agent eindeutig modellieren.
- [ ] Für jedes in der UI dargestellte Fachobjekt eine echte Instanz verwenden.

### Abnahme

- [ ] Domänenobjekte sind unabhängig von Pygame instanziierbar.
- [ ] Zustände werden nicht ausschließlich als lose UI-Texte gehalten.
- [ ] Mindestens zwei Agententypen lassen sich unterscheiden.

---

## 3. Karte und Kartenparser

- [ ] Textkarte beziehungsweise Kartenkonfiguration laden.
- [ ] Eingabe in ein zweidimensionales Grid überführen.
- [ ] Erlaubte Kartenzeichen definieren.
- [ ] Unbekannte Kartenzeichen erkennen und lesbar melden.
- [ ] Kartenbreite validieren.
- [ ] Kartenhöhe validieren.
- [ ] Gleichmäßige Zeilenlängen validieren.
- [ ] Grenzen der Karte korrekt behandeln.
- [ ] Straßen aus der Karte erzeugen.
- [ ] Wände beziehungsweise Hindernisse aus der Karte erzeugen.
- [ ] Depot beziehungsweise Depots aus der Karte erzeugen.
- [ ] Ziele aus der Karte erzeugen.
- [ ] Agentenstartpositionen aus Karte oder Szenario erzeugen.
- [ ] Referenzkarte reproduzierbar laden.
- [ ] Verwendete Karte im Messergebnis identifizierbar machen.

### Tests

- [ ] Gültige Karte wird korrekt geladen.
- [ ] Ungültiges Zeichen wird erkannt.
- [ ] Ungültige Kartengröße wird erkannt.
- [ ] Kartenränder erzeugen keine ungültigen Nachbarn.
- [ ] Depot wird korrekt erkannt.
- [ ] Ziele werden korrekt erkannt.
- [ ] Hindernisse werden korrekt erkannt.

### Abnahme

- [ ] Karte ist im Datenmodell korrekt vorhanden.
- [ ] Karte kann ohne Pygame geladen und geprüft werden.

---

## 4. Nachbarschaft und Bewegung

- [ ] Gültige Nachbarzellen ermitteln.
- [ ] Bewegung außerhalb der Karte verhindern.
- [ ] Bewegung in Wände beziehungsweise Hindernisse verhindern.
- [ ] Bewegung nur auf gültige Zellen zulassen.
- [ ] Deterministischen Simulationsschritt implementieren.
- [ ] Zunächst einfache oder zufällige gültige Bewegung ermöglichen.
- [ ] Zufallsbewegung mit festem Seed reproduzierbar machen.
- [ ] Pro Tick höchstens den vorgesehenen Agentenschritt ausführen.
- [ ] Geschwindigkeit eines Agententyps korrekt berücksichtigen. **[BLATT PRÜFEN]**
- [ ] Kollisionen verhindern beziehungsweise gemäß Aufgabenblatt behandeln. **[BLATT PRÜFEN]**
- [ ] Blockierte Bewegung kontrolliert behandeln.
- [ ] Agentenzustand nach Bewegung aktualisieren.

### Tests

- [ ] Gültige Nachbarn einer freien Zelle stimmen.
- [ ] Nachbarn an Kartenrändern stimmen.
- [ ] Wände erscheinen nicht als gültige Nachbarn.
- [ ] Gültige Bewegung ändert die Position korrekt.
- [ ] Ungültige Bewegung wird abgelehnt.
- [ ] Gleicher Seed erzeugt denselben Ablauf.
- [ ] Mehrere Ticks laufen ohne Pygame durch.

### Abnahme

- [ ] Headless-Simulation kann mehrere Ticks kontrolliert ausführen.
- [ ] Agenten bleiben innerhalb des gültigen Kartenbereichs.

---

## 5. Simulationskern und Tick-Reihenfolge

- [ ] Zentralen Simulationstick implementieren.
- [ ] Tickzähler führen.
- [ ] Eingaben vor der Weltaktualisierung verarbeiten.
- [ ] Neue Aufträge erzeugen oder aus einem Szenario laden.
- [ ] Fällige Ausschreibungen versenden.
- [ ] Nachrichten zustellen.
- [ ] Gebote berechnen.
- [ ] Awards auswerten.
- [ ] Aufträge zuweisen.
- [ ] Pfade planen.
- [ ] Pfade bei Bedarf neu planen. **[BLATT PRÜFEN]**
- [ ] Agenten pro Tick bewegen.
- [ ] Ankunft erkennen.
- [ ] Abschluss erkennen.
- [ ] Fehlerzustände erkennen.
- [ ] Metriken protokollieren.
- [ ] Unveränderlichen beziehungsweise konsistenten Snapshot für Pygame erzeugen.
- [ ] Start beziehungsweise Fortsetzen ermöglichen.
- [ ] Pause ermöglichen.
- [ ] Einzelschritt ermöglichen.
- [ ] Reset auf definierten Ausgangszustand ermöglichen.
- [ ] Simulation kontrolliert beenden.

### Tests

- [ ] Tick erhöht sich genau einmal pro Simulationsschritt.
- [ ] Pause verhindert fachliche Zustandsänderungen.
- [ ] Step führt genau einen Tick aus.
- [ ] Reset stellt den definierten Ausgangszustand wieder her.
- [ ] Tick-Reihenfolge ist deterministisch.

### Abnahme

- [ ] Simulation läuft schrittweise und reproduzierbar.
- [ ] UI und Simulation verwenden denselben konsistenten Zustand.

---

## 6. Aufträge und Auftragslebenszyklus

- [ ] Auftragserzeugung implementieren.
- [ ] Auftrag besitzt eindeutige ID.
- [ ] Auftrag besitzt Start beziehungsweise Depot.
- [ ] Auftrag besitzt Ziel.
- [ ] Auftrag besitzt nachvollziehbaren Status.
- [ ] Auftrag kann angekündigt werden.
- [ ] Auftrag kann vergeben werden.
- [ ] Auftrag kann gestartet werden.
- [ ] Auftrag kann abgeschlossen werden.
- [ ] Auftrag kann kontrolliert fehlschlagen.
- [ ] Gewinner-Agent erhält den Auftrag.
- [ ] Nicht erfolgreiche Bieter bleiben frei beziehungsweise erhalten ihren vorgesehenen Zustand.
- [ ] Ankunft am Ziel aktualisiert den Auftrag korrekt.
- [ ] Auftragsereignisse für spätere Auswertung protokollieren.

### Abnahme

- [ ] Mindestens ein Auftrag durchläuft den vollständigen vorgesehenen Lebenszyklus.
- [ ] Statusänderungen sind im Log und in der UI nachvollziehbar.

---

## 7. Contract-Net-Protokoll

### Verständnis und Spezifikation

- [ ] Contract-Net-Ablauf in eigenen Worten dokumentieren.
- [ ] Manager beziehungsweise Coordinator definieren.
- [ ] Geeignete Bieter beziehungsweise Agenten definieren.
- [ ] Ausschreibung beschreiben.
- [ ] Gebotsbildung beschreiben.
- [ ] Gebotsauswahl beschreiben.
- [ ] Vergabe beschreiben.
- [ ] Ablehnung beschreiben, soweit gefordert. **[BLATT PRÜFEN]**
- [ ] Abschluss beschreiben, soweit gefordert. **[BLATT PRÜFEN]**
- [ ] Fehlerfall beschreiben, soweit gefordert. **[BLATT PRÜFEN]**
- [ ] Tie-Break-Regel eindeutig und reproduzierbar definieren.

### Nachrichten

- [ ] Nachrichtentyp `ANNOUNCE` implementieren.
- [ ] Nachrichtentyp `BID` implementieren.
- [ ] Nachrichtentyp `AWARD` implementieren.
- [ ] Nachrichtentyp `REJECT` implementieren, soweit gefordert. **[BLATT PRÜFEN]**
- [ ] Nachrichtentyp `COMPLETE` implementieren, soweit gefordert. **[BLATT PRÜFEN]**
- [ ] Nachrichtentyp `FAIL` implementieren, soweit gefordert. **[BLATT PRÜFEN]**
- [ ] Absender speichern.
- [ ] Empfänger speichern.
- [ ] Tick beziehungsweise Zeitpunkt speichern.
- [ ] Zugehörige Auftrags-ID speichern.
- [ ] Gebotskosten speichern.
- [ ] Relevante Nachrichtendetails speichern.

### Coordinator und Vergabe

- [ ] Coordinator als eigene Komponente implementieren.
- [ ] Coordinator versendet Ausschreibung.
- [ ] Geeignete Agenten erzeugen Gebote.
- [ ] Ungültige Gebote werden nicht berücksichtigt.
- [ ] Coordinator sammelt Gebote.
- [ ] Coordinator wertet Gebote nach dokumentierter Regel aus.
- [ ] Coordinator bestimmt genau einen Gewinner, sofern gültige Gebote existieren.
- [ ] Gewinner erhält `AWARD`.
- [ ] Verlierer erhalten `REJECT`, sofern gefordert. **[BLATT PRÜFEN]**
- [ ] Kein- Gebot-Fall kontrolliert behandeln.
- [ ] Ausführung mit `COMPLETE` oder kontrolliertem `FAIL` beenden, sofern gefordert. **[BLATT PRÜFEN]**
- [ ] Gesamten Ablauf in den Simulationstick integrieren.
- [ ] Alle relevanten Nachrichten protokollieren.

### Tests

- [ ] Isolierter Test mit drei Agenten und festen Geboten.
- [ ] Niedrigstes gültiges Gebot gewinnt.
- [ ] Gleichstand wird reproduzierbar aufgelöst.
- [ ] Ungültiges Gebot gewinnt nicht.
- [ ] Kein gültiges Gebot wird kontrolliert behandelt.
- [ ] Gewinner erhält Auftrag.
- [ ] Verlierer bleiben frei beziehungsweise werden korrekt zurückgesetzt.
- [ ] Nachrichtenreihenfolge ist nachvollziehbar.

### Abnahme

- [ ] Ein Auftrag wird in der laufenden Simulation nachvollziehbar vergeben.
- [ ] `ANNOUNCE`, `BID` und `AWARD` sind im Log sichtbar.
- [ ] Entscheidung ist mit identischen Eingaben reproduzierbar.

---

## 8. Gebotslogik und Kosten

- [ ] Manhattan-Distanz implementieren.
- [ ] Manhattan-Distanz zunächst als Gebotsmetrik verwenden, sofern vorgesehen.
- [ ] Dokumentieren, wann Manhattan-Distanz und wann reale Pfadkosten verwendet werden.
- [ ] Pfadkosten für Gebote verwenden, wenn das Originalblatt dies verlangt. **[BLATT PRÜFEN]**
- [ ] Agentenverfügbarkeit berücksichtigen, wenn gefordert. **[BLATT PRÜFEN]**
- [ ] Kapazität berücksichtigen, wenn gefordert. **[BLATT PRÜFEN]**
- [ ] Batteriezustand berücksichtigen, wenn gefordert. **[BLATT PRÜFEN]**
- [ ] Eignungsprüfung eines Agenten implementieren.
- [ ] Nicht geeignete Agenten geben kein gültiges Gebot ab.
- [ ] Gebotsberechnung deterministisch halten.

### Tests

- [ ] Manhattan-Distanz für gleiche Position ist null.
- [ ] Manhattan-Distanz für horizontale Strecke stimmt.
- [ ] Manhattan-Distanz für vertikale Strecke stimmt.
- [ ] Manhattan-Distanz für gemischte Strecke stimmt.
- [ ] Nicht geeigneter Agent wird ausgeschlossen.

---

## 9. A\*-Wegfindung

### Algorithmus

- [ ] A\* als eigenständige Komponente implementieren.
- [ ] Priority Queue beziehungsweise priorisierte Open List verwenden.
- [ ] Open Set verwalten.
- [ ] `g_score` verwalten.
- [ ] Zulässige Heuristik verwenden.
- [ ] Manhattan-Distanz als Heuristik im Vier-Nachbarn-Gitter einsetzen.
- [ ] `f(n) = g(n) + h(n)` korrekt berechnen.
- [ ] `came_from` verwalten.
- [ ] Pfad nach Zielerreichung rekonstruieren.
- [ ] Startposition korrekt behandeln.
- [ ] Zielposition korrekt behandeln.
- [ ] Wände beziehungsweise Hindernisse ausschließen.
- [ ] Kartengrenzen beachten.
- [ ] Ergebnis `kein Weg` als regulären Fall behandeln.
- [ ] Kürzesten gültigen Pfad auf Referenzkarten liefern.

### Integration

- [ ] A\*-Pfad nach Auftragsvergabe berechnen.
- [ ] Agent folgt dem berechneten Pfad pro Tick.
- [ ] Pfadfortschritt im Agentenzustand speichern.
- [ ] Ankunft am Ziel erkennen.
- [ ] Bei Ankunft Abschluss auslösen.
- [ ] Pfad bei verändertem Zustand neu planen, falls gefordert. **[BLATT PRÜFEN]**
- [ ] Pfad im Pygame-UI farbig darstellen.
- [ ] Pfadanzeige ein- und ausschaltbar machen.

### Tests

- [ ] Freier direkter Weg wird gefunden.
- [ ] Umweg um eine Wand wird gefunden.
- [ ] Blockiertes Ziel liefert `kein Weg`.
- [ ] Start gleich Ziel liefert einen korrekten trivialen Pfad.
- [ ] Pfad enthält keine Wandzelle.
- [ ] Pfad verlässt die Karte nicht.
- [ ] Auf Referenzkarte ist die Pfadlänge minimal.
- [ ] Agent erreicht entlang des Pfads das Ziel.

### Abnahme

- [ ] Auftrag wird vergeben.
- [ ] A\* plant einen gültigen Pfad.
- [ ] Agent bewegt sich entlang des Pfads.
- [ ] Agent erreicht das Ziel.
- [ ] Abschlussereignis wird erzeugt.

---

## 10. Prolog-Wissensbasis

### Lokale Prolog-Grundlage

- [ ] SWI-Prolog lokal installieren.
- [ ] Miniübung mit Fakt ausführen.
- [ ] Miniübung mit Regel ausführen.
- [ ] Miniübung mit Anfrage ausführen.
- [ ] Positive Anfrage direkt in SWI-Prolog testen.
- [ ] Negative Anfrage direkt in SWI-Prolog testen.

### Wissensbasis

- [ ] Wissensbasis in einer eigenen Datei, zum Beispiel `prolog/world.pl`, anlegen.
- [ ] Geforderte Fakten implementieren. **[BLATT PRÜFEN]**
- [ ] Fakten für Straße abbilden, falls gefordert. **[BLATT PRÜFEN]**
- [ ] Fakten für Wand beziehungsweise Hindernis abbilden, falls gefordert. **[BLATT PRÜFEN]**
- [ ] Fakten für Depot abbilden, falls gefordert. **[BLATT PRÜFEN]**
- [ ] Fakten für Ziel abbilden, falls gefordert. **[BLATT PRÜFEN]**
- [ ] Geforderte Prädikate implementieren. **[BLATT PRÜFEN]**
- [ ] Erreichbarkeitsregel implementieren, falls gefordert. **[BLATT PRÜFEN]**
- [ ] Kleine positive Beispielsituation prüfen.
- [ ] Kleine negative Beispielsituation prüfen.
- [ ] Dokumentieren, welche Entscheidungen Prolog trifft.
- [ ] Dokumentieren, welche Entscheidungen Python trifft.
- [ ] Unbegründete Doppelimplementierung in Python und Prolog vermeiden.

### Abnahme

- [ ] Geforderte Anfrage funktioniert direkt in SWI-Prolog.
- [ ] Positive und negative Fälle liefern die erwarteten Ergebnisse.

---

## 11. Python-Prolog-Integration

- [ ] PySWIP oder den vorgeschriebenen Integrationsweg einrichten. **[BLATT PRÜFEN]**
- [ ] Prolog-Zugriff in einem eigenen Adapter kapseln.
- [ ] Wissensbasis über den Adapter laden.
- [ ] Pro fachlicher Anfrage eine kleine, klar benannte Adaptermethode anbieten.
- [ ] Keine Prolog-Syntax in der restlichen Fachlogik verteilen.
- [ ] Rückgabewerte aus Prolog in geeignete Python-Werte überführen.
- [ ] Fehlende SWI-Prolog-Installation erkennen.
- [ ] Fehlende Prolog-Datei erkennen.
- [ ] Fehlerhafte Prolog-Anfrage kontrolliert behandeln.
- [ ] Fehlermeldungen verständlich ausgeben.
- [ ] Simulation an der geforderten Stelle tatsächlich über Prolog entscheiden lassen. **[BLATT PRÜFEN]**
- [ ] Prolog-Integration früh mit der späteren Build-Variante testen.
- [ ] Nicht-Prolog-Tests weiterhin ohne aktive Prolog-Laufzeit ausführen können.

### Tests

- [ ] Adapter lädt die Wissensbasis.
- [ ] Positive Anfrage über Python funktioniert.
- [ ] Negative Anfrage über Python funktioniert.
- [ ] Fehlende SWI-Prolog-Installation wird kontrolliert behandelt.
- [ ] Fehlende Wissensbasis wird kontrolliert behandelt.
- [ ] Integrationstest deckt die fachlich geforderte Prolog-Entscheidung ab.

### Abnahme

- [ ] Simulation verwendet Prolog an der vorgesehenen Stelle.
- [ ] Prolog-Fehler beenden die Anwendung nicht unkontrolliert.

---

## 12. Pygame-Benutzeroberfläche

### Karte

- [ ] Grid sichtbar darstellen.
- [ ] Straßen sichtbar darstellen.
- [ ] Hindernisse sichtbar darstellen.
- [ ] Depot beziehungsweise Depots sichtbar darstellen.
- [ ] Ziele sichtbar darstellen.
- [ ] Standard-Agenten sichtbar darstellen.
- [ ] Express-Agenten sichtbar darstellen.
- [ ] Agenten-ID sichtbar darstellen.
- [ ] Agententypen farblich unterscheidbar machen.
- [ ] Legende vollständig innerhalb ihres Widgets darstellen.
- [ ] Karte übersichtlich halten.
- [ ] Keine Straßenmarkierungen darstellen.
- [ ] A\*-Pfad sichtbar darstellen.
- [ ] Pfadanzeige schaltbar machen.

### Simulationsstatus

- [ ] Aktuellen Tick anzeigen.
- [ ] Laufmodus anzeigen.
- [ ] Start beziehungsweise Auto sichtbar bedienen können.
- [ ] Pause sichtbar bedienen können.
- [ ] Einzelschritt sichtbar bedienen können.
- [ ] Reset sichtbar bedienen können.
- [ ] Beenden ermöglichen.
- [ ] Simulationsgeschwindigkeit schaltbar beziehungsweise einstellbar machen.

### Agentenstatus

- [ ] Agenten-ID anzeigen.
- [ ] Agententyp anzeigen.
- [ ] Aktuelle Position anzeigen.
- [ ] Zielposition anzeigen.
- [ ] Status anzeigen.
- [ ] Batteriezustand anzeigen, falls relevant. **[BLATT PRÜFEN]**
- [ ] Batteriebalken und Prozentwert ohne Überlagerung nebeneinander anzeigen.
- [ ] Kapazität anzeigen, falls relevant. **[BLATT PRÜFEN]**
- [ ] Ladung anzeigen, falls relevant. **[BLATT PRÜFEN]**
- [ ] Auftrag beziehungsweise Auftragsbezug anzeigen.

### Aufträge und Nachrichten

- [ ] Aktive Aufträge anzeigen.
- [ ] Auftrags-ID anzeigen.
- [ ] Depot beziehungsweise Start anzeigen.
- [ ] Ziel anzeigen.
- [ ] Auftragsstatus anzeigen.
- [ ] Nachrichtenfenster auf relevante Contract-Net-Ereignisse begrenzen.
- [ ] Letzte Nachrichten nachvollziehbar anzeigen.
- [ ] Contract-Net-Log als reine, übersichtliche Tabelle darstellen.
- [ ] Im Contract-Net-Log keine zusätzlichen ANNOUNCE-, BID- oder AWARD-Prozesskästen anzeigen.
- [ ] Logspalten für Tick, Phase, Nachricht beziehungsweise Sender/Empfänger, Auftrag und Details anbieten.
- [ ] Phasen farblich unterscheidbar machen.

### Gestaltungsgrenzen

- [ ] UI als Visualisierung und nicht als eigenständiges Spiel behandeln.
- [ ] Keine unnötige Animation implementieren.
- [ ] Keine Sounds implementieren.
- [ ] Keine komplexe GUI-Technik beginnen, bevor alle Muss-Punkte erfüllt sind.
- [ ] Lesbarkeit vor Dekoration priorisieren.
- [ ] Ein Dritter kann den Ablauf ohne Konsolenlog verstehen.

### Abnahme

- [ ] Alle Kernobjekte sind auf der Karte erkennbar.
- [ ] Alle Texte bleiben innerhalb ihrer Widgets.
- [ ] Keine Texte oder Balken überlagern sich.
- [ ] UI zeigt den tatsächlichen Zustand der Fachobjekte.
- [ ] Steuerung ist ohne Quellcodekenntnis auffindbar.

---

## 13. Ereignisse und Metriken

### Ereigniserfassung

- [ ] Ereignis `Auftrag erstellt` erfassen.
- [ ] Ereignis `Auftrag angekündigt` erfassen.
- [ ] Ereignis `Auftrag vergeben` erfassen.
- [ ] Ereignis `Auftrag gestartet` erfassen.
- [ ] Ereignis `Auftrag abgeschlossen` erfassen.
- [ ] Ereignis `Auftrag fehlgeschlagen` erfassen.
- [ ] Tick beziehungsweise Zeitpunkt jedes Ereignisses speichern.
- [ ] Auftrags-ID jedem Ereignis zuordnen.
- [ ] Agenten-ID zuordnen, sofern relevant.

### Kennzahlen

- [ ] Lieferdauer berechnen.
- [ ] A\*-Laufzeit messen.
- [ ] Nachrichten pro Auftrag zählen.
- [ ] Weglänge messen.
- [ ] Erfolgreiche Aufträge erfassen.
- [ ] Fehlgeschlagene Aufträge erfassen.
- [ ] Erfolgsquote berechnen.
- [ ] Kollisionen erfassen, falls gefordert. **[BLATT PRÜFEN]**
- [ ] Kennzahlen auf Plausibilität prüfen.

### Reproduzierbarkeit

- [ ] Festen Random Seed unterstützen.
- [ ] Seed im Messergebnis speichern.
- [ ] Karte im Messergebnis speichern.
- [ ] Konfiguration im Messergebnis speichern.
- [ ] Gleiche Eingaben erzeugen vergleichbare Ergebnisse.

### Abnahme

- [ ] Ein vollständiger Simulationslauf erzeugt verwertbare Messdaten.
- [ ] Kennzahlen lassen sich einem konkreten Szenario zuordnen.

---

## 14. Szenarien

- [ ] Reproduzierbares einfaches Szenario definieren.
- [ ] Reproduzierbares Hindernisszenario definieren.
- [ ] Reproduzierbares Szenario mit mehreren Agenten und/oder Aufträgen definieren.
- [ ] Für jedes Szenario Karte festlegen.
- [ ] Für jedes Szenario Seed festlegen.
- [ ] Für jedes Szenario Konfiguration festlegen.
- [ ] Für jedes Szenario erwarteten Endzustand dokumentieren.
- [ ] Einfaches Szenario vollständig ausführen.
- [ ] Hindernisszenario vollständig ausführen.
- [ ] Mehragenten-/Mehrauftragsszenario vollständig ausführen.
- [ ] Fehlerfall als eigenes beziehungsweise ergänzendes Szenario demonstrieren.

### Abnahme

- [ ] Jedes Szenario läuft bis zu einem klaren Endzustand.
- [ ] Ergebnisse sind wiederholbar.

---

## 15. CSV-Export und Diagramme

- [ ] Messdaten als CSV exportieren.
- [ ] CSV besitzt verständliche Spaltennamen.
- [ ] CSV enthält Szenario-Kennung.
- [ ] CSV enthält Seed.
- [ ] CSV enthält Karten- beziehungsweise Konfigurationskennung.
- [ ] CSV enthält die geforderten Kennzahlen. **[BLATT PRÜFEN]**
- [ ] CSV-Ausgabe nach einem Gesamtlauf prüfen.
- [ ] Diagramm zur Lieferdauer erzeugen.
- [ ] Diagramm zum Nachrichtenaufwand erzeugen.
- [ ] Diagramm zur Erfolgsquote erzeugen.
- [ ] Weitere ausdrücklich geforderte Diagramme erzeugen. **[BLATT PRÜFEN]**
- [ ] Achsen beschriften.
- [ ] Diagrammtitel ergänzen.
- [ ] Szenarien eindeutig unterscheidbar machen.
- [ ] Diagrammwerte gegen CSV plausibilisieren.
- [ ] Diagramme in einem abgabefähigen Format speichern.

### Abnahme

- [ ] Vollständiger Lauf erzeugt eine CSV-Datei.
- [ ] Mindestens die in der Aufgabenstellung geforderten Diagramme liegen vor. **[BLATT PRÜFEN]**
- [ ] Diagramme sind aus den exportierten Messdaten nachvollziehbar.

---

## 16. Automatisierte Tests

### Karten- und Modelltests

- [ ] Kartenparser-Test vorhanden.
- [ ] Kartenvalidierungstest vorhanden.
- [ ] Nachbarschaftstest vorhanden.
- [ ] Bewegungstest vorhanden.
- [ ] Ticktest vorhanden.
- [ ] Resettest vorhanden.

### Contract-Net-Tests

- [ ] Drei-feste-Gebote-Test vorhanden.
- [ ] Gleichstandstest vorhanden.
- [ ] Ungültiges-Gebot-Test vorhanden.
- [ ] Kein-Gebot-Test vorhanden.
- [ ] Auftragszuweisungstest vorhanden.

### A\*-Tests

- [ ] Freier-Weg-Test vorhanden.
- [ ] Umweg-Test vorhanden.
- [ ] Blockiert-Test vorhanden.
- [ ] Start-ist-Ziel-Test vorhanden.
- [ ] Kürzester-Pfad-Test vorhanden.

### Prolog-Tests

- [ ] Positiver Direkt-Prolog-Test vorhanden.
- [ ] Negativer Direkt-Prolog-Test vorhanden.
- [ ] Adapter-Integrationstest vorhanden.
- [ ] Fehlende-Prolog-Laufzeit-Test beziehungsweise kontrollierter Prüffall vorhanden.

### Gesamtflusstests

- [ ] Vergabe-Bewegung-Ankunft-Abschluss als Regressionslauf vorhanden.
- [ ] Kernfall vollständig getestet.
- [ ] Fehlerfall vollständig getestet.
- [ ] Demo-Szenario läuft bis zu einem klaren Endzustand.
- [ ] Gesamte Testsuite ist grün.
- [ ] Falls ein Test nicht grün ist, Abweichung und Begründung dokumentieren.

---

## 17. Dokumentation

### README

- [ ] Projektzweck erklären.
- [ ] Voraussetzungen nennen.
- [ ] Unterstützte Python-Version nennen.
- [ ] Installation erklären.
- [ ] Start erklären.
- [ ] Bedienung erklären.
- [ ] Start/Pause/Step/Reset erklären.
- [ ] Geschwindigkeitssteuerung erklären.
- [ ] Pfadanzeige erklären.
- [ ] Build-Start erklären.
- [ ] Prolog-Voraussetzung erklären.
- [ ] Typische Fehler und Hilfe dokumentieren.
- [ ] CSV-Ausgabeort dokumentieren.
- [ ] Diagrammausgabe dokumentieren.

### Technische Dokumentation

- [ ] Architektur in eigenen Worten erklären.
- [ ] Trennung von Fachlogik und Pygame erklären.
- [ ] Domänenmodell erklären.
- [ ] Tick-Reihenfolge erklären.
- [ ] Agentenzustände erklären.
- [ ] Auftragslebenszyklus erklären.
- [ ] Contract-Net-Ablauf erklären.
- [ ] Tie-Break-Regel erklären.
- [ ] Gebotskosten erklären.
- [ ] A\*-Algorithmus erklären.
- [ ] Verwendete Heuristik erklären.
- [ ] Kein-Weg-Fall erklären.
- [ ] Prolog-Wissensbasis erklären.
- [ ] Python-Prolog-Verantwortungstrennung erklären.
- [ ] Metrikerfassung erklären.
- [ ] Szenarien erklären.
- [ ] CSV-Struktur erklären.
- [ ] Diagramme erklären.
- [ ] Bekannte Grenzen ehrlich dokumentieren.
- [ ] Wesentliche Architekturentscheidungen im Entscheidungslog dokumentieren.

### Nachweisführung

- [ ] Jede Anforderung mit einem Nachweis verknüpfen.
- [ ] Relevante Tests referenzieren.
- [ ] Relevante Screenshots referenzieren.
- [ ] Relevante Logs referenzieren.
- [ ] Relevante CSV-Dateien referenzieren.
- [ ] Relevante Diagramme referenzieren.
- [ ] Dokumentation stimmt mit dem aktuellen Code überein.

---

## 18. Windows-Build und Startbarkeit

- [ ] PyInstaller konfigurieren.
- [ ] Windows-Ordner-Build erzeugen.
- [ ] Ordner-Build gegenüber One-File bevorzugen, wenn Prolog dadurch stabiler eingebunden wird.
- [ ] Python-Konfigurationen beziehungsweise Szenariodateien in den Build aufnehmen.
- [ ] Prolog-Wissensbasis in den Build aufnehmen.
- [ ] Weitere benötigte Ressourcen in den Build aufnehmen.
- [ ] Relative Ressourcenpfade im Build prüfen.
- [ ] Start ohne Entwicklungs-IDE testen.
- [ ] Start ohne aktivierte virtuelle Umgebung testen.
- [ ] Fehlende externe Laufzeitkomponenten verständlich melden.
- [ ] Build auf sauberem Windows-Benutzerkonto oder zweitem Rechner testen.
- [ ] Anwendung im Clean-System-Test starten.
- [ ] Demo im Clean-System-Test ausführen.
- [ ] Reset im Clean-System-Test ausführen.
- [ ] CSV-Ausgabe im Clean-System-Test prüfen.
- [ ] Anwendung im Clean-System-Test regulär beenden.

### Abnahme

- [ ] Prüfer kann das Paket mit wenigen, klar dokumentierten Schritten starten.
- [ ] Kernfall ist ohne Entwicklungswerkzeuge sichtbar.
- [ ] Externe Prolog-Abhängigkeiten sind entweder enthalten oder eindeutig dokumentiert. **[BLATT PRÜFEN]**

---

## 19. Abgabepaket

- [ ] Anwendungs-Build aufnehmen.
- [ ] Quellcode gemäß Abgabevorgabe aufnehmen. **[BLATT PRÜFEN]**
- [ ] README aufnehmen.
- [ ] Aufgabenmatrix beziehungsweise diese Anforderungsliste aufnehmen.
- [ ] Technische Dokumentation aufnehmen.
- [ ] Beispielkonfiguration aufnehmen.
- [ ] Referenzkarte aufnehmen.
- [ ] Prolog-Dateien aufnehmen.
- [ ] Tests gemäß Vorgabe aufnehmen. **[BLATT PRÜFEN]**
- [ ] Beispiel-CSV aufnehmen, falls sinnvoll oder gefordert. **[BLATT PRÜFEN]**
- [ ] Diagramme aufnehmen, falls gefordert. **[BLATT PRÜFEN]**
- [ ] Screenshots beziehungsweise Nachweise aufnehmen, falls gefordert. **[BLATT PRÜFEN]**
- [ ] Temporäre Dateien entfernen.
- [ ] Virtuelle Umgebung nicht unnötig mitliefern.
- [ ] Python-Caches entfernen.
- [ ] IDE-spezifische Dateien entfernen, sofern nicht benötigt.
- [ ] Alte Builds entfernen.
- [ ] Veraltete Messergebnisse entfernen.
- [ ] Paketstruktur auf Verständlichkeit prüfen.
- [ ] Abgabepaket auspacken und erneut starten.
- [ ] Finale Abnahmecheckliste ausfüllen.

---

## 20. Demonstration

- [ ] Feste Demoabfolge definieren.
- [ ] Demo zeigt Start der Anwendung.
- [ ] Demo zeigt Karte und Agenten.
- [ ] Demo zeigt einen neuen beziehungsweise aktiven Auftrag.
- [ ] Demo zeigt `ANNOUNCE`.
- [ ] Demo zeigt mindestens ein `BID`.
- [ ] Demo zeigt `AWARD`.
- [ ] Demo zeigt A\*-Pfadplanung.
- [ ] Demo zeigt Agentenbewegung.
- [ ] Demo zeigt Zielerreichung.
- [ ] Demo zeigt Abschluss oder Ergebnis.
- [ ] Demo zeigt relevante Metrik beziehungsweise CSV-Ausgabe.
- [ ] Fehlerfall demonstrieren.
- [ ] Reset demonstrieren.
- [ ] Reguläres Beenden demonstrieren.
- [ ] Demoablauf zweimal vollständig proben.

### Abnahme

- [ ] Kernfall ist in einer festen, kurzen Präsentationsabfolge nachvollziehbar.
- [ ] Fehlerfall endet kontrolliert und verständlich.

---

## 21. Scope-Schutz und explizite Nicht-Ziele

Diese Punkte sind nur umzusetzen, wenn das Original-Aufgabenblatt sie ausdrücklich verlangt:

- [ ] **Nicht erforderlich:** Sprite-System.
- [ ] **Nicht erforderlich:** Animationen.
- [ ] **Nicht erforderlich:** Sounds.
- [ ] **Nicht erforderlich:** zusätzliches GUI-Framework.
- [ ] **Nicht erforderlich:** Karteneditor.
- [ ] **Nicht erforderlich:** Drag-and-drop.
- [ ] **Nicht erforderlich:** Theme-System.
- [ ] **Nicht erforderlich:** Installer.
- [ ] **Nicht erforderlich:** Auto-Update.
- [ ] **Nicht erforderlich:** One-File-Build.
- [ ] **Nicht erforderlich:** zusätzliche Szenarien ohne Bewertungsnutzen.
- [ ] **Nicht erforderlich:** aufwendige Icons.
- [ ] **Nicht erforderlich:** dekorative Straßenmarkierungen.
- [ ] **Nicht erforderlich:** visuelle Contract-Net-Prozesskästen zusätzlich zum Log.

---

## 22. Wochenabnahme

### Woche 1: Fundament und Pygame

- [ ] Originalblatt abgeglichen.
- [ ] Projekt startet.
- [ ] Pygame-Grundlagen funktionieren.
- [ ] Domänenmodell ist angelegt.
- [ ] Textkarte wird geladen und validiert.
- [ ] Grid und Kernobjekte werden erzeugt.
- [ ] Deterministischer Tick funktioniert.
- [ ] Gültige Bewegung funktioniert.
- [ ] Karte und Agenten sind sichtbar.
- [ ] Start/Pause, Step, Reset und Exit funktionieren.
- [ ] Karten-, Nachbar-, Bewegungs- und Ticktests sind vorhanden.
- [ ] README ist aktuell.
- [ ] UI und Logik sind getrennt.

### Woche 2: Contract-Net und A\*

- [ ] Contract-Net-Ablauf ist dokumentiert.
- [ ] Nachrichtenmodell ist implementiert.
- [ ] Coordinator ist implementiert.
- [ ] Drei-Gebote-Test funktioniert.
- [ ] Gleichstand wird reproduzierbar behandelt.
- [ ] Manhattan-Kosten funktionieren.
- [ ] Eignungsprüfung funktioniert.
- [ ] `ANNOUNCE -> BID -> AWARD` ist in den Tick integriert.
- [ ] Nachrichten sind im Log nachvollziehbar.
- [ ] A\* ist implementiert.
- [ ] Vier A\*-Referenzfälle sind getestet.
- [ ] Agent folgt dem Pfad.
- [ ] Pfad ist im UI sichtbar.
- [ ] Vergabe, Bewegung, Ankunft und Abschluss funktionieren als Gesamtfluss.

### Woche 3: Prolog und Auswertung

- [ ] SWI-Prolog-Miniübung funktioniert.
- [ ] Wissensbasis ist vorhanden.
- [ ] Geforderte Fakten sind implementiert. **[BLATT PRÜFEN]**
- [ ] Geforderte Regeln beziehungsweise Prädikate sind implementiert. **[BLATT PRÜFEN]**
- [ ] Positive und negative Direktabfrage funktionieren.
- [ ] PrologAdapter ist integriert.
- [ ] Prolog-Fehler werden lesbar behandelt.
- [ ] Prolog-Integrationstest funktioniert.
- [ ] Ereignisse werden erfasst.
- [ ] Geforderte Kennzahlen werden berechnet. **[BLATT PRÜFEN]**
- [ ] Drei reproduzierbare Szenarien laufen.
- [ ] CSV wird erzeugt.
- [ ] Diagramme werden erzeugt.
- [ ] Messwerte sind plausibilisiert.

### Woche 4: Abgabequalität

- [ ] UI ist lesbar und vollständig.
- [ ] Legende ist vollständig sichtbar.
- [ ] Agentenstatus ist vollständig sichtbar.
- [ ] Contract-Net-Log ist übersichtlich.
- [ ] Geschwindigkeit ist schaltbar.
- [ ] Pfadanzeige ist schaltbar.
- [ ] Alle Tests wurden ausgeführt.
- [ ] Gesamtfluss wurde geprüft.
- [ ] Fehlerfall wurde geprüft.
- [ ] README ist vollständig.
- [ ] Architektur ist dokumentiert.
- [ ] A\* ist dokumentiert.
- [ ] Contract-Net ist dokumentiert.
- [ ] Prolog ist dokumentiert.
- [ ] Messung und Grenzen sind dokumentiert.
- [ ] Aufgabenliste beziehungsweise Matrix ist aktuell.
- [ ] Windows-Ordner-Build ist erzeugt.
- [ ] Clean-System-Test ist bestanden.
- [ ] Kernfall wurde demonstriert.
- [ ] Fehlerfall wurde demonstriert.
- [ ] CSV-Ausgabe wurde im Build geprüft.
- [ ] Abgabepaket ist bereinigt.

---

## 23. Finale Definition of Done

Das Projekt ist erst vollständig abgeschlossen, wenn alle hier zutreffenden Punkte erfüllt sind:

- [ ] Original-Aufgabenblatt ist vollständig abgeglichen.
- [ ] Alle Muss-Anforderungen sind umgesetzt.
- [ ] Jede Muss-Anforderung besitzt einen überprüfbaren Nachweis.
- [ ] Ein reproduzierbarer Simulationslauf mit fester Karte und festem Seed funktioniert.
- [ ] Mindestens zwei Agententypen sind umgesetzt.
- [ ] Agentenzustände sind nachvollziehbar.
- [ ] Aufträge werden nachvollziehbar bearbeitet.
- [ ] Contract-Net protokolliert mindestens `ANNOUNCE`, `BID` und `AWARD`.
- [ ] A\* findet auf den Referenzkarten einen gültigen kürzesten Pfad.
- [ ] Manhattan-Distanz wird korrekt als Heuristik beziehungsweise vorgesehene Gebotsmetrik verwendet.
- [ ] Prolog enthält die geforderten Fakten und Regeln. **[BLATT PRÜFEN]**
- [ ] Prolog wird über einen gekapselten Adapter abgefragt.
- [ ] Pygame zeigt Karte, Agenten, Ziele, A\*-Pfad, Simulationsstatus und Nachrichten.
- [ ] Messdaten werden als CSV exportiert.
- [ ] Geforderte Diagramme liegen vor. **[BLATT PRÜFEN]**
- [ ] Automatisierte Tests sind grün oder begründete Abweichungen sind dokumentiert.
- [ ] README ermöglicht einen verständlichen Start.
- [ ] Windows-Build startet auf einem sauberen System.
- [ ] Kernfall und Fehlerfall sind demonstrierbar.
- [ ] Abgabepaket enthält nur aktuelle, benötigte Bestandteile.

---

## 24. Offene Punkte aus dem Originalblatt

Diese Tabelle nach dem Abgleich mit dem Original-Aufgabenblatt ausfüllen:

| ID | Originalanforderung | Muss/Kann | Umsetzung | Abnahmekriterium | Nachweis | Status |
|---|---|---|---|---|---|---|
| O-01 | Noch abzugleichen |  |  |  |  | ⬜ |
| O-02 | Noch abzugleichen |  |  |  |  | ⬜ |
| O-03 | Noch abzugleichen |  |  |  |  | ⬜ |
| O-04 | Noch abzugleichen |  |  |  |  | ⬜ |
| O-05 | Noch abzugleichen |  |  |  |  | ⬜ |

---

## 25. Fortschrittsnotizen

### Aktueller Fokus

- [ ] Aufgabe 1: UI-Grundgerüst und sichtbare Kartenobjekte

### Entscheidungen

- 20 x 20 Grid.
- Pygame als Visualisierung.
- Keine Straßenmarkierungen.
- Legende vollständig innerhalb des Kartenpanels.
- Batteriebalken und Prozentwert getrennt.
- Contract-Net ausschließlich als tabellarisches Log, ohne zusätzliche Prozesskästen.
- Fachobjekte als Klassen mit echten Instanzen in der UI.

### Nächster Schritt

- [ ] Diese Liste mit dem Original-Aufgabenblatt abgleichen und alle **[BLATT PRÜFEN]**-Markierungen auflösen.
