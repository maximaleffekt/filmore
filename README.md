# filmore

filmore ist eine kleine Flask‑Webanwendung zur Verwaltung analoger Filmrollen, Aufnahmen sowie der persönlichen Ausrüstung (Kameras, Objektive, Filter). Die Anwendung bietet Benutzer‑Registrierung/-Anmeldung, das Anlegen von Rollen (Filmtyp, ISO) und das Erfassen einzelner Aufnahmen mit Metadaten und optionalem Upload eines Bildes. Die Projektdateien enthalten Jinja2‑Templates, statische Assets und ein SQLite‑Datenbank‑Backend.

## Wichtige Features

- Benutzer-Authentifizierung (Flask‑Login)
- Rollenverwaltung (Filmrolle mit Hersteller, Typ, ISO)
- Erfassen von Aufnahmen/Frames mit Blende, Verschlusszeit, Kamera/Objektiv/Filter‑Auswahl
- Verwaltung von Kameras, Objektiven und Filtern
- JSON‑Export einer Rolle (Download)

## Voraussetzungen

- Python 3.8+ (empfohlen 3.10+)
- pip

Die Abhängigkeiten sind in `requirements.txt` im Projektstamm festgehalten.

## Konfiguration

Die Anwendung verwendet standardmäßig eine lokale SQLite‑Datenbank `database.db` (konfiguriert in `app.py`).

- `app.config['SECRET_KEY']` sollte in Produktion immer über eine Umgebungsvariable gesetzt werden.
- In `app.py` sind Cookie‑Sicherheitsoptionen gesetzt (z. B. `SESSION_COOKIE_SECURE=True`). Bei lokaler Entwicklung ohne HTTPS kannst du diese temporär auf `False` setzen.

## Projektstruktur

- `app.py` – Haupt‑App, Routen und Konfiguration
- `models.py` – Datenbankmodelle (SQLAlchemy)
- `forms.py` – WTForms‑Formulare
- `templates/` – Jinja2‑Templates (z. B. `index.html`, `add_image.html`)
- `static/` – statische Dateien (CSS, Service‑Worker, `uploads/`)
- `instance/` – optionaler Ordner für lokale Konfigurationen

## Anwendung starten 

Standardmäßig lauscht die App auf `0.0.0.0:5001` (siehe `app.py`). Beim Start werden die Datenbanktabellen automatisch mit `db.create_all()` angelegt.

## Hinweise für Produktivbetrieb

- Setze `SECRET_KEY` und andere sensible Werte sicher (z. B. Environment‑Variablen, Secrets‑Manager).
- Verwende eine Produktions‑WSGI‑Lösung wie Gunicorn oder uWSGI hinter einem Reverse‑Proxy (z. B. Nginx).
- Aktiviere HTTPS und setze `SESSION_COOKIE_SECURE=True`.
- Nutze eine robuste Datenbank (Postgres, MySQL) anstelle von SQLite bei mehreren gleichzeitigen Nutzern.

## Entwicklung / Troubleshooting

- Upload‑Ordner: `static/uploads` wird beim Start angelegt (siehe `app.py`).
- Wenn Templates nicht gefunden werden: überprüfe, dass `templates/` im Projektstamm liegt.
- Fehlende Python‑Pakete: Installieren, siehe `requirements.txt`.
