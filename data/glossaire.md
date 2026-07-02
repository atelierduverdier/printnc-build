# A - B - C

## ATC (Changeur d'outil automatique)
Système mécanique et logiciel permettant à la machine de changer d'outil seule. Sur cette PrintNC, un ATC a été testé mais jugé "pas assez costaud". La solution retenue est un changement manuel couplé à un palpage automatique de la longueur (semi-automatique).

## Backlash (Jeu mécanique)
Jeu résiduel dans une transmission (entre la vis à billes et son écrou, ou dans un couplage). Se traduit par une imprécision lors des inversions de sens. Sur cette PrintNC, il est minimisé par la qualité des vis à billes et peut être compensé dans la configuration LinuxCNC via le paramètre `BACKLASH`.

## BF12 / BK12
Supports d'extrémité pour vis à billes. BK12 = support fixe (côté moteur, palier rigide), BF12 = support flottant (côté opposé, palier qui peut glisser légèrement pour compenser la dilatation thermique de la vis).

## BOM (Bill of Materials)
Nomenclature ou liste des matériaux. Désigne le tableau récapitulatif de toutes les pièces, visserie et composants nécessaires à la construction de la machine, avec leur prix.

## Boucle fermée (Closed loop)
Mode de fonctionnement d'un moteur pas à pas équipé d'un encodeur. Contrairement à la boucle ouverte (où les pas perdus ne sont pas détectés), le driver vérifie en permanence que la position réelle correspond à la position commandée. Sur cette PrintNC, les drivers CL57T v4.1 fonctionnent en boucle fermée avec les Nema 23.

## Broche (Spindle)
Moteur électrique dédié à la rotation de l'outil de coupe. Ici, une G-Penny 2.2 kW refroidie par eau, avec une pince ER20, pouvant monter jusqu'à 24 000 tr/min. Pilotée par un VFD.

## CAM (Computer-Aided Manufacturing)
Logiciel de génération de parcours d'outils à partir d'un modèle 3D. Produit le G-code envoyé à LinuxCNC. Sur cette PrintNC, FreeCAD (avec l'atelier Path) est utilisé.

## Capteur inductif
Capteur de proximité sans contact (ici LJ8A3-2-Z/AX) utilisé pour les fins de course. Il détecte la présence d'un métal à proximité. Configuré en NPN NC (Normalement Fermé, logique active basse).

## CL57T
Référence du driver utilisé sur cette PrintNC (CL57T v4.1, omc-stepperonline). Driver hybride en boucle fermée pour moteurs Nema 23. Alimentation 24-48 V, courant 0.8-7 A. Quatre exemplaires sur la machine (X, Y1, Y2, Z).

# D - E - F

## Driver (Pilote de moteur)
Composant électronique qui convertit les signaux de pas/direction (provenant de la carte FlexiHAL) en courant suffisant pour faire tourner les moteurs pas à pas. Ici, des CL57T v4.1 en boucle fermée.

## Encodeur
Capteur magnétique ou optique fixé sur l'arbre du moteur qui mesure la rotation réelle. Permet le fonctionnement en boucle fermée. Sur cette PrintNC, chaque moteur Nema 23 dispose d'un encodeur magnétique 1000 PPR (4000 CPR en quadrature). Le driver CL57T lit l'encodeur et peut détecter une perte de pas.

## ER20 (Pince / Collet)
Système de serrage d'outil à cône élastique. "ER" = système standardisé, "20" = diamètre extérieur de la pince en mm. L'ER20 accepte des queues d'outil de 1 à 13 mm. C'est le type de pince monté sur la broche G-Penny de cette machine.

## Équerrage (Squaring)
Réglage visant à rendre les axes X et Y parfaitement perpendiculaires (à 90°). Réalisé avant le serrage définitif des vis de structure, souvent via la méthode du triangle 3-4-5 ou des pins.

## FlexiHAL
Carte de contrôle CNC conçue par Expatria, exécutant le firmware Remora. Communique avec le Raspberry Pi par bus SPI et génère les impulsions des moteurs en matériel.

## FreeCAD
Logiciel open source de CAO (Conception Assistée par Ordinateur) et CAM. Utilisé sur cette PrintNC pour dessiner les pièces à usiner et générer les parcours d'outils (atelier Path) qui produisent le G-code.

# G - H - L

## G-code
Langage de programmation numérique standard utilisé pour piloter les machines CNC (ex: `G0 X10 Y20` pour un déplacement rapide, `M3 S12000` pour lancer la broche à 12000 tr/min).

## G54 (Système de coordonnées pièce)
L'un des systèmes de coordonnées de travail (WCS) de LinuxCNC. Définit le zéro pièce par rapport à l'origine machine. Activé par défaut au démarrage. Le "touch off" définit ce zéro. G53 permet de se déplacer en coordonnées machine absolues, indépendamment de G54.

## GrblHAL
Firmware open source pour machines CNC, dérivé de GRBL. La FlexiHAL supporte à la fois GrblHAL et LinuxCNC (via Remora). Cette PrintNC utilise LinuxCNC/Remora.

## HAL (Hardware Abstraction Layer)
Système propre à LinuxCNC. C'est un langage de câblage logique (fichiers `.hal`) qui permet de connecter les signaux physiques (boutons, capteurs) aux fonctions logicielles (mouvements, pauses) via des composants comme `and2`, `or2` ou `not`.

## HGR20 / HGW20CC
Rail linéaire de guidage de type HIWIN (ou copie). "HGR20" = référence du rail (largeur 20 mm), "HGW20CC" = référence du chariot (patin) qui glisse dessus, modèle large à bride. Utilisés sur les trois axes de la PrintNC.

## Homing (Référencement)
Procédure de démarrage qui permet à la machine de trouver ses origines physiques (capteurs de fin de course) pour connaître sa position exacte. Sur cette machine, le Z monte en premier pour éviter les collisions.

## HYComm
Protocole de communication série propriétaire utilisé par les variateurs Huanyang (VFD). Ce n'est pas du Modbus RTU standard, bien qu'il utilise la même liaison physique (RS485).

## LinuxCNC
Logiciel open source de contrôle CNC tournant sur Linux temps-réel (PREEMPT_RT ou RTAI). C'est le "cerveau" de la machine : il interprète le G-code, calcule les trajectoires, gère les axes et communique avec la FlexiHAL via Remora/SPI. Ici utilisé sur Raspberry Pi 5.

# M - N - P

## MDI (Manual Data Input)
Mode de LinuxCNC permettant d'entrer et d'exécuter des commandes G-code manuellement, une ligne à la fois, sans charger de fichier programme. Utile pour les déplacements ponctuels ou les tests.

## Modbus RTU
Protocole de communication industriel standard sur liaison RS485. Le VFD Huanyang de cette machine utilise HYComm, qui ressemble à Modbus RTU mais n'est pas compatible avec lui.

## Nema 23
Standard de taille définissant l'interface de fixation d'un moteur pas à pas (front de 57.15 x 57.15 mm). Ici, modèles 23HS40-5004-ME1K en boucle fermée (3.00 Nm).

## Palpeur (Tool Setter)
Dispositif de mesure fixe monté sur la table de la machine. Lors d'un changement d'outil, la broche descend lentement, touche le palpeur, et LinuxCNC calcule la longueur exacte du nouvel outil par différence.

## Portique (Gantry)
Structure en pont mobile portant l'axe X et la broche. Sur une PrintNC, le portique se déplace sur l'axe Y via deux rails linéaires et deux vis à billes (configuration Tandem Y).

## PPR / CPR
Pulses Per Revolution / Counts Per Revolution. Mesure de la résolution d'un encodeur. Un encodeur 1000 PPR donne 4000 CPR en mode quadrature (4 fronts détectés par impulsion mécanique). Les Nema 23 de cette machine ont des encodeurs 1000 PPR / 4000 CPR.

## PrintNC
Fraiseuse CNC open source conçue pour être construite avec des profils acier standards, des rails linéaires HGR et des vis à billes SFU. "Print" réfère aux pièces de liaison imprimées en 3D, "NC" à "Numerical Control". Projet communautaire, documentation sur wiki.printnc.info.

## PySide6
Ensemble de bibliothèques Python permettant de créer des interfaces graphiques (GUI). Utilisé ici pour l'outil `gestion_site.py` qui génère et gère le site web.

# Q - R - S

## QtDragon
Interface graphique (GUI) complète pour LinuxCNC, écrite en Python (PyQt/PySide). Ici, la version "HD" est utilisée et personnalisée pour ajouter des boutons personnalisés (relais, caméra, etc.).

## Rail linéaire (HGR20)
Guidage linéaire de précision à billes recirculantes. Composé d'un rail fixe (HGR20) et d'un ou plusieurs chariots (HGW20CC) qui glissent dessus avec très peu de jeu. Sur cette PrintNC, un seul patin par rail a été choisi (contre deux habituellement) pour simplifier le montage.

## Remora
Firmware open source installé sur la FlexiHAL (microcontrôleur RP2040). Il reçoit les ordres du Raspberry Pi via bus SPI et génère les impulsions de pas en matériel à haute fréquence, déchargeant le Pi de cette tâche temps-réel critique.

## REMAP
Fonctionnalité de LinuxCNC permettant de redéfinir le comportement d'un code M standard (comme M6 pour le changement d'outil) pour lui faire exécuter un script personnalisé (fichier `.ngc`).

## RS485
Norme de communication série différentielle utilisée pour connecter le Raspberry Pi au VFD sur de longues distances sans parasite. Nécessite un adaptateur USB-RS485.

## Runout (Faux-rond)
Défaut de perpendicularité de l'axe de la broche par rapport à son corps. Un runout élevé provoque des vibrations et des usures prématurées de l'outil. Mesuré avec un comparateur.

## SFU1204 / SFU1610
Références de vis à billes. "SFU" = ball screw à brides, "16" = diamètre 16 mm, "10" = pas de 10 mm/tour. Le SFU1204 (axe Z) a un diamètre de 12 mm et un pas de 4 mm pour plus de précision et d'auto-freinage. Le SFU1610 (axes X et Y) offre plus de rigidité.

## SPI (Serial Peripheral Interface)
Bus de communication série rapide reliant le Raspberry Pi à la FlexiHAL. Synchrone, jusqu'à plusieurs dizaines de MHz. Permet l'échange en temps-réel des consignes de position et des états des entrées/sorties entre le Pi et la carte de contrôle.

## StepGen
Générateur de pas (composant LinuxCNC/HAL). Il génère la fréquence exacte d'impulsions pour faire tourner les moteurs à la vitesse demandée par le G-code.

## Surfaçage (Facing / Surfacing)
Opération d'usinage consistant à passer la fraise sur toute la surface d'une pièce pour obtenir une surface plane et de référence. Sur cette PrintNC, utilisé pour mettre la table à niveau et préparer les pièces en aluminium.

# T - V

## Tandem Y
Configuration mécanique où l'axe Y est entraîné par deux moteurs distincts (Y1 et Y2), un de chaque côté du portique. Cela évite les problèmes de désynchronisation des courroies ou des arbres de liaison.

## Touch off
Opération qui définit le zéro pièce (G54) à la position actuelle de l'outil ou de la machine. Se fait manuellement en approchant l'outil d'un coin de pièce (papier cigarette), ou automatiquement via le palpeur pour la longueur d'outil.

## Tramming
Opération de réglage consistant à rendre l'axe de la broche parfaitement perpendiculaire à la table de la machine (réglage autour de X et Y). Indispensable pour faire des perçages ronds et non ovales.

## VFD (Variateur de Fréquence)
Appareil électronique (ici Huanyang 2.2 kW) qui convertit le courant secteur (230V 50Hz) en courant de fréquence variable pour contrôler la vitesse de rotation d'un moteur alternatif (la broche).

## Vis à billes (Ball screw)
Mécanisme de transmission convertissant un mouvement rotatif (moteur) en mouvement linéaire (axe). Composé d'une vis hélicoïdale et d'un écrou contenant des billes recirculantes. Bien plus précis et efficace qu'une vis trapézoïdale : rendement ~90% contre ~30-40%, et jeu quasi nul.

# W - Z

## WCS (Work Coordinate System)
Système de coordonnées de travail. Dans LinuxCNC, G54 à G59 définissent jusqu'à 6 WCS différents, permettant de mémoriser plusieurs origines pièce sans avoir à refaire le touch off. G53 désigne les coordonnées machine absolues.

# G-code — Guide de référence (FR)

> Cette section est une référence pratique en français. Les exemples sont concrets et adaptés à l'utilisation d'une fraiseuse CNC comme cette PrintNC (bois, aluminium).

## Les déplacements : G0, G1, G2, G3

**G0 — Déplacement rapide** (sans usinage, vitesse maximale de la machine)

```
G0 Z5          ; Monter l'outil à Z=5 mm (dégagement sécurité)
G0 X0 Y0       ; Aller en X0 Y0 en rapide
G0 X50 Y30 Z2  ; Aller à cette position en rapide (les 3 axes bougent en même temps)
```

**G1 — Déplacement en travail** (usinage, vitesse contrôlée par F en mm/min)

```
G1 Z-3 F300    ; Plonger à -3 mm à 300 mm/min
G1 X100 F800   ; Avancer de X=100 à 800 mm/min en fraisant
G1 X100 Y50 F600  ; Déplacement diagonal en fraisage
```

**G2 — Arc de cercle sens horaire** (vu de dessus)
**G3 — Arc de cercle sens anti-horaire**

Deux façons de définir un arc :

Avec I et J (coordonnées du centre, relatives au point de départ) :
```
; Cercle complet de rayon 20 mm (départ et arrivée au même point)
G0 X20 Y0
G1 Z-2 F300
G2 X20 Y0 I-20 J0 F500   ; I=-20 = le centre est à X-20 par rapport au départ
```

Avec R (rayon, plus simple pour les demi-cercles) :
```
G0 X0 Y0
G1 Z-2 F300
G2 X40 Y0 R20 F500   ; Arc CW de rayon 20 passant de X0 à X40
```

> **Astuce PrintNC** : toujours faire un G0 Z5 avant de se déplacer en rapide vers un nouveau point, pour ne pas raser la pièce ou les brides.

## Les espaces de travail : G54–G59 et G53

La machine a deux types de coordonnées :
- **Coordonnées machine** (G53) : origine physique fixe, définie par le homing. Ne change jamais.
- **Coordonnées pièce** (G54 à G59) : origine que tu choisis sur ta pièce (le "zéro pièce"). C'est là que tu travailles.

**G54 à G59 — Six origines pièce mémorisables**

```
G54   ; Activer le système de coordonnées 1 (par défaut au démarrage)
G55   ; Activer le système 2 (pratique pour une 2ème pièce sur la table)
G56   ; Système 3 — etc.
```

Concrètement : tu poses ta pièce, tu fais un touch off pour dire "ici c'est X0 Y0 Z0", et LinuxCNC mémorise ça dans G54. La prochaine fois que tu charges la même pièce au même endroit, tu rappelles juste G54.

**G53 — Se déplacer en coordonnées machine** (utile pour aller à un point fixe quelle que soit l'origine pièce)

```
G53 G0 Z0      ; Monter l'axe Z à son maximum physique (Z=0 machine = en haut)
G53 G0 X0 Y0   ; Aller à l'origine machine en X et Y
```

> **Attention** : G53 est une action unique (non-modale). La ligne suivante revient automatiquement au WCS actif (G54 ou autre).

**G10 — Définir un WCS par G-code** (sans passer par l'interface)

```
G10 L2 P1 X0 Y0 Z0   ; Réinitialiser G54 (P1) à la position actuelle
G10 L2 P2 X100 Y0    ; Décaler l'origine de G55 de 100 mm en X
```

`L2` = modifier le WCS, `P1` = G54, `P2` = G55, etc.

## Positionnement absolu / relatif : G90 et G91

**G90 — Mode absolu** (par défaut, toujours recommandé) : les coordonnées sont relatives à l'origine pièce.

```
G90
G0 X10   ; Aller à X=10 mm depuis l'origine
G0 X50   ; Aller à X=50 mm depuis l'origine
```

**G91 — Mode relatif** : les coordonnées sont des déplacements depuis la position courante.

```
G91
G0 X10   ; Avancer de 10 mm depuis où on est
G0 X10   ; Avancer encore de 10 mm (on est maintenant à X=20)
G90      ; Toujours revenir en absolu après !
```

> **Conseil** : travailler en G90 autant que possible. G91 est utile pour des répétitions ou des mouvements relatifs rapides (ex: `G91 G1 Z-1 F200` pour plonger de 1 mm supplémentaire), mais oublier de remettre G90 est une source classique d'erreurs.

## Unités et plan de travail : G20, G21, G17

```
G21   ; Unités en millimètres (toujours utiliser ça en Europe)
G20   ; Unités en pouces (pour les fichiers G-code américains)

G17   ; Plan de travail XY (fraisage standard, broche sur Z — c'est le défaut)
G18   ; Plan XZ (utilisé pour des arcs dans le plan vertical X/Z)
G19   ; Plan YZ
```

## Contrôle de la broche : M3, M4, M5

```
M3 S12000   ; Lancer la broche sens horaire à 12000 tr/min
M4 S8000    ; Lancer la broche sens anti-horaire à 8000 tr/min (rare)
M5          ; Arrêter la broche
```

> **Sur cette PrintNC** : la vitesse mini utile est ~6000 tr/min (en dessous, le VFD Huanyang n'a plus de couple), et le maxi est 24000 tr/min. Pour l'aluminium, 12000–18000 tr/min est typique. Pour le bois, 18000–24000 tr/min.

## Changement d'outil : M6, T

```
T2 M6    ; Demander l'outil n°2 et effectuer le changement
```

Sur cette PrintNC, M6 est remappé (REMAP) pour déclencher une procédure automatique : l'opérateur change l'outil manuellement, puis la machine palpe automatiquement la longueur. Le programme attend que tu confirmes avant de reprendre.

```
T1 M6    ; Outil 1 (fraise de 6 mm)
M3 S18000
G43 H1   ; Appliquer l'offset de longueur de l'outil 1
```

## Refroidissement : M7, M8, M9

```
M7   ; Brouillard (mist coolant) — petit jet d'air + gouttelettes
M8   ; Arrosage (flood coolant) — jet d'eau/huile continu
M9   ; Arrêter le refroidissement
```

> Sur cette PrintNC, M7 et M8 contrôlent des relais câblés sur la carte FlexiHAL. M8 peut être branché sur un souffleur d'air pour évacuer les copeaux sans mouiller la pièce.

## Offsets de longueur d'outil : G43, G49

Quand tu changes d'outil, le nouvel outil n'a pas la même longueur. G43 dit à la machine de tenir compte de cette différence pour que Z0 reste au même endroit sur ta pièce.

```
G43 H1   ; Appliquer l'offset de longueur mémorisé dans le slot H1
G43 H0   ; Offset nul (outil de référence)
G49      ; Annuler l'offset de longueur
```

> Sur cette PrintNC, le palpeur automatique met à jour H automatiquement après chaque M6. Tu n'as donc jamais à écrire G43 manuellement si tu utilises le changement d'outil standard.

## Cycles de perçage : G81, G83, G80

**G81 — Perçage simple** (descente d'un coup, remontée)

```
G81 X10 Y10 Z-15 R2 F150   ; Percer à X10 Y10, profondeur -15 mm, plan de dégagement R=2 mm
G81 X30 Y10                  ; Percer un 2ème trou (même profondeur et F)
G80                           ; Annuler le cycle de perçage
```

**G83 — Perçage par débourrage** (descend par paliers, remonte pour évacuer les copeaux — essentiel pour l'aluminium)

```
G83 X10 Y10 Z-20 R2 Q3 F100
; Z-20 = profondeur finale
; R2   = plan de dégagement (remonte à Z=2 entre chaque passe)
; Q3   = profondeur de chaque passe (3 mm à la fois)
; F100 = avance en mm/min
G83 X40 Y10   ; Idem sur un 2ème point
G80           ; Annuler
```

## Pause et fin de programme : M0, M1, M2, M30

```
M0    ; Pause inconditionnelle — le programme s'arrête, attend CYCLE START
M1    ; Pause optionnelle (active seulement si "OPT STOP" est coché dans l'interface)
M2    ; Fin de programme (réinitialise les modes G-code)
M30   ; Fin de programme + retour au début du fichier (équivalent à M2 en pratique)
```

> **Astuce** : mettre un `M0` avant un changement d'outil manuel pour avoir le temps de changer la fraise calmement. `M0` avec un commentaire c'est encore mieux :
> ```
> M0 (Changer pour fraise 3mm et reprendre)
> ```

## Temporisation : G4

```
G4 P2.5   ; Attendre 2.5 secondes (utile après M3 pour laisser la broche monter en vitesse)
```

## Divers utiles

**G28 — Retour à la position de référence** (définie dans la config LinuxCNC, souvent X0 Y0 Z0 machine)
```
G28 Z0   ; Monter Z à sa position de référence avant tout (sécurité)
```

**F et S — Changer vitesse d'avance et de broche en cours de programme**
```
F1200      ; Changer l'avance à 1200 mm/min (sans autre mouvement)
S20000     ; Changer la vitesse broche à 20000 tr/min (sans la relancer)
M3 S20000  ; Relancer la broche à la nouvelle vitesse
```

**Commentaires** : entre parenthèses, ignorés par la machine
```
G0 X0 Y0   (retour à l'origine pièce)
M5         (arrêt broche — on a fini)
```

## Tableau récapitulatif

| Code | Rôle | Exemple |
|------|------|---------|
| G0 | Déplacement rapide | `G0 X0 Y0 Z5` |
| G1 | Déplacement en travail | `G1 X50 F800` |
| G2 | Arc sens horaire | `G2 X20 Y0 R10 F400` |
| G3 | Arc sens anti-horaire | `G3 X0 Y20 R10 F400` |
| G4 | Temporisation | `G4 P1.5` |
| G10 | Définir WCS | `G10 L2 P1 X0 Y0 Z0` |
| G17 | Plan XY (défaut) | `G17` |
| G20 | Unités pouces | `G20` |
| G21 | Unités mm | `G21` |
| G28 | Retour référence | `G28 Z0` |
| G43 | Offset longueur outil | `G43 H1` |
| G49 | Annuler offset outil | `G49` |
| G53 | Coordonnées machine | `G53 G0 Z0` |
| G54–G59 | Origines pièce | `G54` |
| G80 | Annuler cycle perçage | `G80` |
| G81 | Perçage simple | `G81 X10 Y10 Z-15 R2 F150` |
| G83 | Perçage débourrage | `G83 Z-20 R2 Q3 F100` |
| G90 | Mode absolu (défaut) | `G90` |
| G91 | Mode relatif | `G91` |
| M0 | Pause programme | `M0` |
| M2 / M30 | Fin de programme | `M30` |
| M3 | Broche sens horaire | `M3 S18000` |
| M4 | Broche sens anti-horaire | `M4 S8000` |
| M5 | Arrêt broche | `M5` |
| M6 | Changement d'outil | `T2 M6` |
| M7 | Brouillard | `M7` |
| M8 | Arrosage | `M8` |
| M9 | Arrêt refroidissement | `M9` |

## Exemple complet : début de programme type PrintNC

```
%
; Fraisage d'un contour sur bois — fraise 6mm 2 dents
G21 G90 G17       ; mm, mode absolu, plan XY
G54               ; Utiliser l'origine pièce 1
G53 G0 Z0         ; Monter Z au maximum machine (sécurité)
T1 M6             ; Outil 1 : fraise 6mm
G43 H1            ; Appliquer l'offset de longueur
M3 S20000         ; Broche à 20000 tr/min
G4 P3             ; Attendre 3s que la broche monte en vitesse
G0 X0 Y0          ; Aller à l'origine pièce
G0 Z2             ; Descendre à 2mm au-dessus de la pièce
G1 Z-3 F300       ; Plonger à -3mm à 300 mm/min
G1 X100 F1200     ; Usiner le premier côté
G1 Y50            ; Deuxième côté
G1 X0             ; Troisième côté
G1 Y0             ; Retour au départ
G0 Z10            ; Dégagement
M5                ; Arrêt broche
G53 G0 Z0         ; Z au maximum
G53 G0 X0 Y0      ; Retour origine machine
M30               ; Fin de programme
%
```

## Exemple complet : perçage de 3 trous dans l'aluminium

```
%
G21 G90 G17
G54
G53 G0 Z0
T2 M6             ; Foret 5mm
G43 H2
M3 S3000          ; Vitesse lente pour le perçage alu
G4 P2
G0 X10 Y10        ; Se positionner au-dessus du 1er trou
G0 Z2             ; Dégagement à 2mm
G83 Z-12 R2 Q2 F80  ; Perçage débourrage : profondeur 12mm, passes de 2mm
X30 Y10           ; 2ème trou (même paramètres)
X50 Y30           ; 3ème trou
G80               ; Fin du cycle de perçage
G0 Z10
M5
G53 G0 Z0
M30
%
```
