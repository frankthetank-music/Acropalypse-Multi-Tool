# Verwenden eines offiziellen Python-Laufzeit-Images als Eltern-Image
FROM python:3.10

# Arbeitsverzeichnis im Container setzen
WORKDIR /usr/src/app

# Abhängigkeiten installieren
# Kopieren der Datei 'requirements.txt' ins Container-Verzeichnis '/usr/src/app'
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren des Quellcodes ins Container-Verzeichnis '/usr/src/app'
COPY . .

# Befehl, der beim Start des Containers ausgeführt wird
CMD [ "python", "./gui.py" ]
