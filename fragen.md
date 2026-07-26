# Fragen zum Web UI / Dashboard

## Verständnis
Du möchtest ein Web-Dashboard (entweder per EXE oder direkt im Backend),
das den Status der "Services" anzeigt — ob sie online oder offline sind.

## Offene Fragen

1. **Welche Services?**
   - Nur der PC Power Control Backend selbst?
   - Oder auch andere Dienste im Netzwerk (z.B. NAS, andere PCs, Docker-Container)?

2. **Wie soll es laufen?**
   - **Variante A:** Einfache HTML-Seite, die vom bestehenden FastAPI-Server auf `http://localhost:5000/` mitausgeliefert wird (kein EXE nötig, öffnest du einfach im Browser).
   - **Variante B:** Separates EXE (z.B. mit PyInstaller gebaut), das ein Browser-Fenster öffnet.
   - **Variante C:** Ein Python-Script, das eine lokale HTML-Datei generiert und im Browser öffnet.

3. **Was soll auf dem Dashboard stehen?**
   - Backend-Status (CPU, RAM, Laufzeit)
   - Aktiver Power-Plan
   - Aktiver Mode (Download/Silent/...)
   - Netzwerk-Ping-Status zu anderen IPs?
   - Etwas anderes?

4. **Soll man Aktionen aus dem Dashboard auslösen können?**
   - Z.B. Shutdown/Restart/Sleep per Klick?
   - Mode-Wechsel per Klick?
   - Nur lesend (read-only Dashboard)?

## Meine Empfehlung
**Variante A** — Static HTML Dashboard vom Backend serviert:
- Minimaler Aufwand (kein EXE-Build, kein neuer Server)
- Läuft sofort auf `http://localhost:5000/`
- Keine extra Installation für den Nutzer
- Kann später immer noch in ein EXE verpackt werden (PyInstaller)
