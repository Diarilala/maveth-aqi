<<<<<<< HEAD
# maveth-aqi ARCHITECTURE

## Orchestrateur : GitHub Actions + cron-job.org

Un workflow implémenté dans GitHub qui push les données acquises directement sans actions intermediaires: Github Actions configure le fonctionnement mais puisque Github Actions utilise un systeme de fil d'attente, la liaison avec cron-job assure que le script soit exécuté tous les heures et non lorsque l'action est disponible dans GitHub Actions, ce qui resout le probleme d'un orchestrateur auto-hébergé comme Airflow qui necéssite une machine du groupe constamment allumée.

## Stockage brut (raw/) : fichiers JSON versionnés dans le dépôt Git

Chaque appel API est sauvegardé tel quel (un fichier par ville et par
appel) dans `raw/<ville>/<période>.json`, sans jamais être modifié après
écriture. Ce choix garantit une trace brute immuable de chaque collecte,
et l'historique Git des commits sert lui-même de preuve d'exécution
automatisée et régulière du pipeline.

## Emplacement scripts (src/) : un dossier dédié pour tous les codes nécessaires

Un emplacement dédié pour les scripts facilitent grandement la lisibilité du code et permet de comprendre directement le role de chaque partie du code.
=======
# Architecture

- **API** : OpenWeatherMap Air Pollution API — gratuite, historique disponible, couvre l'AQI et les polluants nécessaires (CO, NO, NO2, O3, SO2, PM2.5, PM10, NH3)

- **Villes** (5 minimum) : Hanoi (VN), Manila (PH), Taipei (TW), Tunis (TN), Vancouver (CA) — diversité de zones géographiques et de profils de pollution

- **Orchestrateur** : GitHub Actions (workflow cron horaire) — natif au repo, gratuit, aucun serveur à héberger, historique des runs directement visible dans l'onglet Actions du repo

- **Stockage raw/clean** : fichiers versionnés dans le repo Git
  - `raw/` : un fichier JSON par ville et par appel, jamais modifié après écriture
  - `clean/` : un fichier CSV unique (`air_quality.csv`), entièrement reconstruit à chaque exécution depuis `raw/`

- **Warehouse** : PostgreSQL hébergé sur **Neon** — base serverless gratuite, accessible en ligne via connection string, scaling à zéro entre les runs.

- **Langage** : Python (`requests`, `pandas`, `python-dotenv`, `sqlalchemy`/`psycopg2`) — une seule stack pour toute l'équipe

- **Modélisation** : schéma en étoile — cas simple, pas de hiérarchies justifiant un schéma en flocon
  - `fact_air_quality` : aqi, co, no, no2, o3, so2, pm2_5, pm10, nh3, fk_time, fk_city
  - `dim_time` : date, heure, jour_semaine, weekend_bool, mois, année
  - `dim_city` : nom, pays, latitude, longitude
  - Script de création des tables : `sql/init.sql`
  - Script de chargement : `src/load_warehouse.py`
>>>>>>> 2b9ee0c (chore : write ARCHITECTURE.md with justication)
