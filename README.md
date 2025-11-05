## Weather Forecaster - Guide de démarrage Kafka KRaft (Windows)

Ce guide permet à toute personne de cloner le projet et de démarrer Kafka (mode KRaft) en quelques commandes avec PowerShell.

### 1) Prérequis
- Windows 10/11, PowerShell.
- Java 17+ installé (vérifier: `java -version`).
- Python 3.10+ installé.
- Accès admin facultatif (pour le premier lancement et les scripts).

### 2) Installer Kafka (une seule fois)
1. Télécharger Kafka binaire (Scala 2.13) depuis le site Apache Kafka.
2. Extraire et placer le dossier à `C:\kafka`.

### 3) Configurer Kafka KRaft (une seule fois)
Dans `C:\kafka\config\kraft\server.properties`, vérifier/modifier:

```
process.roles=broker,controller
node.id=1
controller.quorum.voters=1@localhost:9093
listeners=PLAINTEXT://:9092,CONTROLLER://:9093
inter.broker.listener.name=PLAINTEXT
controller.listener.names=CONTROLLER
log.dirs=C:/kafka/kraft-combined-logs
num.partitions=1
offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
group.initial.rebalance.delay.ms=0
```

Important: utiliser des `/` dans `log.dirs` sous Windows pour éviter les soucis d’échappement.

### 4) Préparer l’environnement Python
Dans le dossier du projet:
```
cd C:\Users\majid\Documents\weather-forecaster
python -m venv venv
.\n+venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
(Adapter si votre fichier `requirements.txt` évolue.)

### 5) Démarrer Kafka (options simples)
Depuis la racine du projet:

```
.
scripts\start_kafka.ps1
```

- Pour voir les logs dans la même fenêtre (bloquant, Ctrl+C pour arrêter):

```
.
scripts\start_kafka.ps1 -Attach
```

- Si première fois ou après erreur/plantage (nettoyage et reformatage):

```
.
scripts\start_kafka.ps1 -Clean
```

Le script gère:
- la génération/récupération du cluster.id (KRaft),
- le formatage idempotent du stockage,
- le démarrage du broker,
- une vérification automatique du port 9092 (mode non-attaché).

### 6) Créer/assurer les topics requis
Toujours depuis la racine du projet:

```
.
scripts\create_topics.ps1
```

Topics concernés:
- `data.raw.weather`
- `data.cleaned.weather`
- `data.features.weather`
- `data.predictions.weather`

### 7) Vérifier que Kafka écoute
```
Test-NetConnection -ComputerName localhost -Port 9092
```

### 8) Lancer le backend (exemples)
- Django:
```
cd .\backend
python manage.py runserver
```

- FastAPI (exemple):
```
cd .\backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 9) Dépannage
- Erreur `Invalid cluster.id` ou logs corrompus:
  - `.
  scripts\start_kafka.ps1 -Clean`
- Kafka ne s’ouvre pas ou 9092 fermé:
  - vérifier `log.dirs` (utiliser `C:/kafka/kraft-combined-logs`),
  - relancer avec `-Clean`.
- Exécution des scripts bloquée:
  - ouvrir PowerShell en admin et exécuter: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 10) Récap des commandes quotidiennes
```
cd C:\Users\majid\Documents\weather-forecaster
.
venv\Scripts\Activate.ps1
.
scripts\start_kafka.ps1 -Attach   # pour voir les logs
.
scripts\create_topics.ps1         # (si besoin)
```

### 11) Arrêt
- Mode attaché: Ctrl+C
- Mode fenêtre séparée: fermer la fenêtre Java démarrée ou tuer le processus Java dans le Gestionnaire des tâches.


