#!/bin/bash
# Dieses Script versteckt den Mauszeiger nach 5 Sekunden Inaktivität
# Voraussetzung: 'unclutter' muss installiert sein (sudo apt-get install unclutter)

# Prüfen ob unclutter läuft, wenn ja, killen um mehrfache Ausführung zu verhindern
pkill unclutter

# Unclutter starten:
# -idle 5: Verstecken nach 5 Sekunden
# -root: Auf dem gesamten Bildschirm (Root Window)
echo "Starte unclutter (versteckt Maus nach 5s)..."
unclutter -idle 5 -root &
