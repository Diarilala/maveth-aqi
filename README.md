# maveth-aqi README - Stockage

## Villes choisies

| Ville | Latitude | Longitude |
|---|---|---|
| Hanoi | 21.0285 | 105.8048 |
| Manila | 14.6534 | 120.9986 |
| Taipei | 25.0330 | 121.5607 |
| Tunis | 36.8065 | 10.1815 |
| Vancouver | 49.2827 | -123.1207 |

## raw/

- Un fichier JSON par ville et par appel API, jamais modifié après écriture.
- Backfill : `raw/<ville_slug>/<début>_<fin>.json` (fenêtres de 20 jours, réponse brute de l'endpoint historique AQI d'OpenWeatherMap).
- Collecte horaire (GitHub Actions) : `raw/<ville_slug>/<horodatage>.json` (réponse brute de l'endpoint AQI courant).
- Période couverte par le backfill : 12 mois avant la mise en production de la collecte horaire.
- Trous connus : 
    + Le comportement du scheduler de Github Actions n'est pas un planificateur cron mais une file d'attente ce qui fait que le script ne se lance pas aux heures prevues et peut etre en attente pendant au moins 1 heure