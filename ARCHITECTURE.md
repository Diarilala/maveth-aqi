# maveth-aqi ARCHITECTURE

## Orchestrateur : GitHub Actions + cron-job.org

Un workflow implemente dans GitHub qui push les donnees acquises directement sans actions intermediaires: Github Actions configure le fonctionnement mais puisque Github Actions utilise un systeme de fil d'attente, la liaison avec cron-job assure que le script soit executer tous les heures et non quand l'action est disponible dans GitHub Actions, ce qui resout le probleme d'un orchestrateur auto-hébergé comme Airflow qui necessite une machine du groupe constamment allumee.

## Stockage brut (raw/) : fichiers JSON versionnés dans le dépôt Git

Chaque appel API est sauvegardé tel quel (un fichier par ville et par
appel) dans `raw/<ville>/<période>.json`, sans jamais être modifié après
écriture. Ce choix garantit une trace brute immuable de chaque collecte,
et l'historique Git des commits sert lui-même de preuve d'exécution
automatisée et régulière du pipeline.

## Emplacement scripts (src/) : un dossier dedie pour tous les codes necessaires

Un emplacement dedie pour les scripts facilitent grandement la lisibilite du code et permet de comprendre directement le role de chaque partie du code.