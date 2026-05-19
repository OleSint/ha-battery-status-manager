# Battery Status Manager — Documentation (Français)

> **Retour à :** [README](../README.md) | [EN](en.md) | [DE](de.md) | [NL](nl.md) | [ES](es.md)

---

## Table des matières

1. [À quoi sert cette intégration ?](#1-à-quoi-sert-cette-intégration-)
2. [Prérequis](#2-prérequis)
3. [Installation](#3-installation)
4. [Configuration initiale](#4-configuration-initiale)
5. [Périmètre de surveillance](#5-périmètre-de-surveillance)
6. [Seuils](#6-seuils)
7. [Notifications](#7-notifications)
8. [Rapport hebdomadaire](#8-rapport-hebdomadaire)
9. [Modifier les paramètres ultérieurement](#9-modifier-les-paramètres-ultérieurement)
10. [Fonctionnement des notifications (détails techniques)](#10-fonctionnement-des-notifications-détails-techniques)
11. [Dépannage](#11-dépannage)

---

## 1. À quoi sert cette intégration ?

Battery Status Manager surveille tous les appareils alimentés par batterie dans votre Home Assistant et vous notifie lorsqu'une action est nécessaire. Elle est conçue pour être configurée une seule fois, puis fonctionner silencieusement en arrière-plan.

Fonctionnalités principales :

- Envoie une **alerte** lorsqu'une batterie passe sous un niveau configurable (ex. 20 %).
- Envoie une **alerte critique** lorsqu'une batterie atteint un niveau très bas (ex. 10 %).
- Détecte une **décharge rapide** (ex. perte de 20 % en 24 heures) et vous alerte immédiatement.
- Inclut une **prévision d'épuisement** dans chaque notification — l'intégration estime combien de jours il reste avant que la batterie soit vide, en se basant sur le taux de décharge mesuré.
- Envoie des **rappels** à intervalles configurables si une batterie reste faible.
- Génère optionnellement un **rapport de synthèse hebdomadaire** le jour et à l'heure de votre choix.
- Respecte une **plage horaire** et des **jours actifs**, pour ne pas être dérangé à 3 h du matin.

---

## 2. Prérequis

- Home Assistant **2023.6** ou version ultérieure.
- Au moins un **service de notification** configuré dans Home Assistant (ex. application mobile officielle, bot Telegram, notificateur email). Ces services apparaissent sous la forme `notify.votre_service` dans Home Assistant.

---

## 3. Installation

### Via HACS (recommandé)

HACS est le Home Assistant Community Store. Si vous ne l'avez pas encore, suivez le [guide d'installation de HACS](https://hacs.xyz/docs/use/download/download/).

1. Ouvrez HACS dans la barre latérale de Home Assistant.
2. Allez dans **Intégrations**.
3. Cliquez sur le menu trois points (⋮) en haut à droite et choisissez **Dépôts personnalisés**.
4. Collez `https://github.com/OleSint/ha-battery-status-manager` et sélectionnez **Intégration** comme catégorie. Cliquez sur **Ajouter**.
5. Fermez la fenêtre. Recherchez **Battery Status Manager** dans la liste des intégrations HACS.
6. Cliquez dessus, puis sur **Télécharger** (en bas à droite).
7. **Redémarrez Home Assistant** (Paramètres → Système → Redémarrer).

### Installation manuelle

1. Téléchargez le fichier ZIP de la dernière version depuis [GitHub Releases](https://github.com/OleSint/ha-battery-status-manager/releases).
2. Décompressez-le et copiez le dossier `custom_components/battery_status_manager` dans le répertoire `config/custom_components/` de votre installation Home Assistant.
3. Redémarrez Home Assistant.

---

## 4. Configuration initiale

Après le redémarrage :

1. Allez dans **Paramètres → Appareils et services**.
2. Cliquez sur **+ Ajouter une intégration** (en bas à droite).
3. Recherchez **Battery Status Manager** et cliquez dessus.
4. Suivez l'assistant de configuration (4 étapes, décrites ci-dessous).

---

## 5. Périmètre de surveillance

La première étape de l'assistant vous permet de choisir quelles batteries surveiller.

### Option A — Toutes les batteries

Surveille toutes les entités Home Assistant ayant la classe d'appareil `battery`. C'est l'option la plus simple et elle inclut automatiquement les nouveaux appareils ajoutés ultérieurement.

Après avoir choisi « Toutes », vous pouvez optionnellement **exclure** certaines entités (par exemple un capteur de batterie défectueux qui affiche toujours 0 %).

### Option B — Par appareil

Vous voyez la liste de tous les appareils disposant d'au moins une entité batterie. Sélectionnez un ou plusieurs appareils. Seules les entités batterie des appareils sélectionnés sont surveillées.

### Option C — Par entité

Vous voyez la liste de toutes les entités batterie dans Home Assistant. Sélectionnez précisément celles à surveiller.

---

## 6. Seuils

### Seuil d'alerte (⚠️)

- **Activer l'alerte batterie faible** — Activez cette option pour recevoir une notification lorsqu'une batterie passe sous le seuil d'alerte.
- **Seuil d'alerte (%)** — Le pourcentage en dessous duquel l'alerte est envoyée. Valeur par défaut : 20 %.

### Seuil critique (🚨)

- **Activer l'alerte critique** — Activez cette option pour recevoir une deuxième notification plus urgente à un niveau très bas.
- **Seuil critique (%)** — Doit être inférieur au seuil d'alerte. Valeur par défaut : 10 %.

### Détection de décharge rapide

- **Activer la notification de décharge rapide** — Activez cette option pour être alerté d'une décharge anormalement rapide.
- **Seuil de décharge (%)** — Nombre de points de pourcentage perdus pour déclencher l'alerte. Exemple : 20 %.
- **Fenêtre d'observation (heures)** — Sur combien d'heures la perte est mesurée. Exemple : 24 heures.

---

## 7. Notifications

### Services de notification

Sélectionnez quels services `notify.*` doivent recevoir les notifications. Plusieurs choix possibles. Au moins un est requis.

### Titre de la notification

Le titre qui apparaît dans les notifications push ou les emails. Par défaut : `Battery Status Manager`.

### Plage horaire (optionnel)

Activez cette option pour restreindre les notifications à une plage horaire précise.

- **Début de la plage horaire** — Heure la plus tôt à laquelle une notification peut être envoyée. Exemple : `08:00`.
- **Fin de la plage horaire** — Heure la plus tard. Exemple : `20:00`.

Les plages nocturnes sont gérées correctement : début `22:00` et fin `07:00` autorise les notifications entre 22h et 7h.

> Les notifications supprimées parce qu'elles se situent en dehors de la plage horaire **ne sont pas mises en file d'attente** — elles sont simplement ignorées. La prochaine vérification (une heure plus tard) réévaluera la situation.

### Jours actifs (optionnel)

Choisissez les jours de la semaine pendant lesquels les notifications peuvent être envoyées. Par défaut, les sept jours sont actifs.

### Rappel (optionnel)

- **Activer le rappel** — Si une batterie reste sous le seuil après la première notification, un rappel est envoyé après l'intervalle configuré.
- **Intervalle de rappel (heures)** — Fréquence des rappels. Exemple : 24 heures.

Le rappel respecte également la plage horaire et les jours actifs.

---

## 8. Rapport hebdomadaire

Le rapport hebdomadaire est entièrement optionnel. Lorsqu'il est activé, l'intégration envoie un résumé une fois par semaine.

- **Activer le rapport hebdomadaire** — Active le rapport.
- **Jour de la semaine** — Quel jour le rapport est envoyé (ex. lundi).
- **Heure du rapport** — À quelle heure (ex. 09:00).

### Contenu du rapport

- Nombre total de batteries surveillées.
- Nombre de batteries actuellement sous le seuil d'alerte.
- Nombre de batteries actuellement sous le seuil critique.
- Nombre de batteries ayant récupéré ou été remplacées au cours des 7 derniers jours.
- Prévision sur 7 jours : batteries actuellement au-dessus du seuil mais susceptibles de le franchir dans les 7 prochains jours.

Le rapport est envoyé au maximum une fois par période de 7 jours.

---

## 9. Modifier les paramètres ultérieurement

Tous les paramètres peuvent être modifiés à tout moment :

1. Allez dans **Paramètres → Appareils et services**.
2. Trouvez la carte **Battery Status Manager**.
3. Cliquez sur **Configurer**.
4. Parcourez à nouveau l'assistant — vos valeurs précédentes sont pré-remplies.

---

## 10. Fonctionnement des notifications (détails techniques)

### Intervalle de vérification

L'intégration vérifie tous les niveaux de batterie toutes les **60 minutes**.

### Hystérésis

Pour éviter les notifications répétées pour le même événement :

- Une batterie sous le **seuil d'alerte** déclenche une alerte. Elle n'en déclenche pas d'autre tant qu'elle n'est pas remontée au-dessus de `seuil d'alerte + 5 %`.
- Une batterie sous le **seuil critique** déclenche une alerte critique. Elle n'en déclenche pas d'autre tant qu'elle n'est pas remontée au-dessus de `seuil critique + 3 %`.

### Prévision d'épuisement

L'intégration stocke un historique des relevés de batterie. À partir d'au moins 3 points de données sur au moins 2 heures, elle calcule un taux de décharge linéaire et extrapole le nombre de jours restants.

### Stockage des données

Toutes les données d'état sont stockées dans le fichier `.storage/battery_status_manager` de Home Assistant et persistent après les redémarrages.

---

## 11. Dépannage

**Aucune notification reçue**
- Vérifiez qu'un service `notify.*` est correctement configuré et sélectionné.
- Vérifiez la plage horaire et les jours actifs.
- Le niveau de batterie doit être sous le seuil au moment de la vérification horaire.

**Trop de notifications**
- L'hystérésis est active par défaut. Vérifiez si le niveau de batterie oscille autour du seuil.

**Une entité n'apparaît pas dans la liste de sélection**
- Seules les entités avec la classe d'appareil `battery` et une valeur numérique (0–100) sont incluses.

**Le rapport hebdomadaire n'arrive pas**
- Le rapport est envoyé au maximum une fois tous les 7 jours. Vérifiez le jour et l'heure configurés.

**Autre problème**
- Consultez les journaux de Home Assistant (Paramètres → Système → Journaux) et recherchez `battery_status_manager`.
- Ouvrez un ticket sur [GitHub](https://github.com/OleSint/ha-battery-status-manager/issues).
