# Architecture

- **API** : OpenWeatherMap Air Pollution API — gratuite, historique disponible, couvre l'AQI et les polluants nécessaires (CO, NO, NO2, O3, SO2, PM2.5, PM10, NH3)

- **Villes** (5 minimum) : Hanoi (VN), Manila (PH), Taipei (TW), Tunis (TN), Vancouver (CA) — diversité de zones géographiques et de profils de pollution

- **Orchestrateur** : GitHub Actions (workflow cron horaire) + [cron-job.org](https://cron-job.org) — GitHub Actions configure et exécute le pipeline, gratuit et sans serveur à héberger. Mais GitHub Actions utilise un système de file d'attente : le déclenchement horaire n'est pas garanti à l'heure pile. cron-job.org appelle le workflow via son `workflow_dispatch` toutes les heures pour forcer une exécution régulière, réglant ce problème sans dépendre d'une machine du groupe allumée en continu (contrairement à un orchestrateur auto-hébergé comme Airflow).

- **Stockage raw/clean** : fichiers versionnés dans le repo Git
  - `raw/` : un fichier JSON par ville et par appel, jamais modifié après écriture — cette trace brute immuable sert aussi de preuve : l'historique des commits Git montre l'exécution automatisée et régulière du pipeline
  - `clean/` : un fichier CSV unique (`air_quality.csv`), entièrement reconstruit à chaque exécution depuis `raw/`

- **Organisation du code (`src/`)** : un dossier dédié pour tous les scripts (`collect.py`, `backfill.py`, `transform.py`, `load_warehouse.py`) — facilite la lisibilité et permet de comprendre directement le rôle de chaque partie du pipeline

- **Warehouse** : PostgreSQL hébergé sur **Neon** — base serverless gratuite, accessible en ligne via connection string, scaling à zéro entre les runs, facile à partager (correcteur, cours IA1)

- **Langage** : Python (`requests`, `pandas`, `python-dotenv`, `sqlalchemy`/`psycopg2`) — une seule stack pour toute l'équipe

- **Modélisation** : schéma en étoile — cas simple, pas de hiérarchies justifiant un schéma en flocon
  - `fact_air_quality` : aqi, co, no, no2, o3, so2, pm2_5, pm10, nh3, fk_time, fk_city
  - `dim_time` : date, heure, jour_semaine, weekend_bool, mois, année
  - `dim_city` : nom, pays, latitude, longitude
  - Script de création des tables : `sql/init.sql`
  - Script de chargement : `src/load_warehouse.py`