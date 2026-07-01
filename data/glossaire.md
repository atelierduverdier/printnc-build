```markdown
# A - B - C

## ATC (Changeur d'outil automatique)
Système mécanique et logiciel permettant à la machine de changer d'outil seule. Sur cette PrintNC, un ATC a été testé mais jugé "pas assez costaud". La solution retenue est un changement manuel couplé à un palpage automatique de la longueur (semi-automatique).

## BOM (Bill of Materials)
Nomenclature ou liste des matériaux. Désigne le tableau récapitulatif de toutes les pièces, visserie et composants nécessaires à la construction de la machine, avec leur prix.

## Broche (Spindle)
Moteur électrique dédié à la rotation de l'outil de coupe. Ici, une G-Penny 2.2 kW refroidie par eau, avec une pince ER20, pouvant monter jusqu'à 24 000 tr/min. Pilotée par un VFD.

## Capteur inductif
Capteur de proximité sans contact (ici LJ8A3-2-Z/AX) utilisé pour les fins de course. Il détecte la présence d'un métal à proximité. Configuré en NPN NC (Normalement Fermé, logique active basse).

# D - E - F

## Driver (Pilote de moteur)
Composant électronique qui convertit les signaux de pas/direction (provenant de la carte FlexiHAL) en courant suffisant pour faire tourner les moteurs pas à pas. Ici, des CL57T v4.1 en boucle fermée.

## Équerrage (Squaring)
Réglage visant à rendre les axes X et Y parfaitement perpendiculaires (à 90°). Réalisé avant le serrage définitif des vis de structure, souvent via la méthode du triangle 3-4-5 ou des pins.

## FlexiHAL
Carte de contrôle CNC conçue par Expatria, exécutant le firmware Remora. Communique avec le Raspberry Pi par bus SPI et génère les impulsions des moteurs en matériel.

# G - H - L

## G-code
Langage de programmation numérique standard utilisé pour piloter les machines CNC (ex: `G0 X10 Y20` pour un déplacement rapide, `M3 S12000` pour lancer la broche à 12000 tr/min).

## HAL (Hardware Abstraction Layer)
Système propre à LinuxCNC. C'est un langage de câblage logique (fichiers `.hal`) qui permet de connecter les signaux physiques (boutons, capteurs) aux fonctions logicielles (mouvements, pauses) via des composants comme `and2`, `or2` ou `not`.

## Homing (Référencement)
Procédure de démarrage qui permet à la machine de trouver ses origines physiques (capteurs de fin de course) pour connaître sa position exacte. Sur cette machine, le Z monte en premier pour éviter les collisions.

## HYComm
Protocole de communication série propriétaire utilisé par les variateurs Huanyang (VFD). Ce n'est pas du Modbus RTU standard, bien qu'il utilise la même liaison physique (RS485).

# M - N - P

## Nema 23
Standard de taille définissant l'interface de fixation d'un moteur pas à pas (front de 57.15 x 57.15 mm). Ici, modèles 23HS40-5004-ME1K en boucle fermée (3.00 Nm).

## Palpeur (Tool Setter)
Dispositif de mesure fixe monté sur la table de la machine. Lors d'un changement d'outil, la broche descend lentement, touche le palpeur, et LinuxCNC calcule la longueur exacte du nouvel outil par différence.

## PySide6
Ensemble de bibliothèques Python permettant de créer des interfaces graphiques (GUI). Utilisé ici pour l'outil `gestion_site.py` qui génère et gère le site web.

# Q - R - S

## QtDragon
Interface graphique (GUI) complète pour LinuxCNC, écrite en Python (PyQt/PySide). Ici, la version "HD" est utilisée et personnalisée pour ajouter des boutons personnalisés (relais, caméra, etc.).

## REMAP
Fonctionnalité de LinuxCNC permettant de redéfinir le comportement d'un code M standard (comme M6 pour le changement d'outil) pour lui faire exécuter un script personnalisé (fichier `.ngc`).

## RS485
Norme de communication série différentielle utilisée pour connecter le Raspberry Pi au VFD sur de longues distances sans parasite. Nécessite un adaptateur USB-RS485.

## Runout (Faux-rond)
Défaut de perpendicularité de l'axe de la broche par rapport à son corps. Un runout élevé provoque des vibrations et des usures prématurées de l'outil. Mesuré avec un comparateur.

## StepGen
Générateur de pas (composant LinuxCNC/HAL). Il génère la fréquence exacte d'impulsions pour faire tourner les moteurs à la vitesse demandée par le G-code.

# T - V

## Tandem Y
Configuration mécanique où l'axe Y est entraîné par deux moteurs distincts (Y1 et Y2), un de chaque côté du portique. Cela évite les problèmes de désynchronisation des courroies ou des arbres de liaison.

## Tramming
Opération de réglage consistant à rendre l'axe de la broche parfaitement perpendiculaire à la table de la machine (réglage autour de X et Y). Indispensable pour faire des perçages ronds et non ovales.

## VFD (Variateur de Fréquence)
Appareil électronique (ici Huanyang 2.2 kW) qui convertit le courant secteur (230V 50Hz) en courant de fréquence variable pour contrôler la vitesse de rotation d'un moteur alternatif (la broche).
```
