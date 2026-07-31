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