# 2 juillet 2026 — Corrections, liens de partage, vote et glossaire

## Corrections de bugs dans generer_site.py

Trois bugs bloquants corrigés dans le script de génération :

**Page d'accueil invisible au démarrage** : toutes les sections (`#accueil`, `#tl`, etc.) sont masquées par défaut en CSS. La fonction `switchTab` n'était jamais appelée au chargement, donc rien ne s'affichait. Ajout de `switchTab(initHash || 'accueil')` à la fin du script, avec gestion du hash d'URL pour le deep linking.

**Timeline qui ne s'affichait pas** : `switchTab` utilisait `sections.tl.style.display = ''` pour afficher la timeline, mais le CSS définit `#tl { display: none }` — retirer le style inline laissait le CSS reprendre le dessus. Corrigé en utilisant `classList.add('show')` / `classList.remove('show')` comme pour les autres sections.

**Liens de partage non fonctionnels** : découle du bug précédent — ouvrir une URL avec un hash (`#all`, `#2026-06`) n'activait aucun onglet car `switchTab` n'était pas appelée au chargement. Résolu par l'initialisation au démarrage et un listener `hashchange`.

**Bonus** : suppression d'un `<div id="tabs-mois">` vide généré en doublon dans le HTML (vestige du template).

## Liens de partage par ancre (🔗)

Ajout de boutons de partage discrets sur l'ensemble du site, visibles au survol :

- **Chaque étape vidéo** reçoit un identifiant unique (`id="v-nomfichier"`) et un bouton 🔗 dans la ligne de méta-données.
- **Chaque en-tête de mois** dispose d'un bouton 🔗 pour partager directement une période.
- **Chaque section de documentation et de glossaire** reçoit un identifiant slugifié (`id="doc-lubrification"` etc.) et un bouton 🔗 positionné dans l'accordéon.

Un clic copie l'URL directe dans le presse-papier et affiche un toast "Lien copié !". Au chargement, le script détecte le hash et navigue automatiquement : `#v-nomfichier` ouvre la timeline et scrolle vers l'étape, `#doc-nom-section` ouvre l'onglet Documentation et déplie la section concernée.

## Widget vote repensé

**Nouvelle question** : "Vous construisez (ou envisagez) une PrintNC ?" avec bouton "Oui, je me lance !" au lieu de "Ce contenu vous a-t-il été utile ?" / "Utile". La question mesure l'intention plutôt que la satisfaction — plus engageante et plus informative.

**Compteur affiché** : au chargement, le widget lit le compteur GoatCounter via l'API publique `/counter/%2Fvote-utile.json` et affiche le nombre de votants ("42 personnes se lancent aussi !"). Les messages s'adaptent selon le contexte : déjà voté, premier votant, juste après le clic. Aucun backend supplémentaire requis.

## Glossaire complété

**Correction d'un bug** : `data/glossaire.md` était enveloppé dans des balises ` ```markdown ` ... ` ``` `, ce qui affichait tout le contenu comme un bloc de code brut. Suppression des balises parasites.

**Nouveaux termes** : environ 20 entrées ajoutées (Backlash, BF12/BK12, Boucle fermée, CL57T, Encodeur, ER20, FreeCAD, G54/WCS, GrblHAL, HGR20/HGW20CC, LinuxCNC, MDI, Modbus RTU, Portique, PPR/CPR, PrintNC, Rail linéaire, Remora, SFU1204/SFU1610, SPI, Surfaçage, Touch off, Vis à billes) en plus des 22 existantes.

**Nouvelle section G-code** : référence complète en français — déplacements (G0/G1/G2/G3), espaces de travail (G54–G59/G53), positionnement (G90/G91), broche (M3/M4/M5), changement d'outil (M6), refroidissement (M7/M8/M9), cycles de perçage (G81/G83/G80), offsets outil (G43/G49), pause et fin (M0/M2/M30), temporisation (G4). Tableau de 29 codes + deux exemples complets commentés (contour sur bois, perçage alu avec débourrage).

# 30 juin 2026 — Évolution majeure du site web (Recherche, jalons, glossaire, durées)
## Recherche en temps réel et Deep Linking
Ajout d'une barre de recherche sur la timeline. L'input filtre les 246+ vidéos instantanément par titre, légende ou contenu, sans rechargement de page. Ajout du Deep Linking (modification du hash de l'URL via history.replaceState) : cliquer sur un mois ou un onglet met à jour l'URL (ex: #2026-06), ce qui permet de copier/coller un lien direct vers une période spécifique. Au chargement, le script JS vérifie window.location.hash et active l'onglet correspondant. Ajout d'un bouton "Remonter" (back-to-top) flottant en bas à droite, visible après 600 px de scroll.

## Jalons visuels et durées des vidéos
Deux nouvelles colonnes duree et jalon dans videos.csv. Si jalon est à oui, l'étape apparaît avec un fond orange subtil et une bordure gauche distincte dans la timeline pour mettre en valeur les moments forts (premier montage, premiers copeaux, carte grillée...). Si duree est renseignée (format MM:SS), un badge noir est affiché en bas à droite de la miniature.

Pour éviter de remplir les durées à la main, création du script remplir_durees.py. Il parcourt le CSV, localise chaque vidéo dans videos_sources/, extrait la durée via ffprobe (requête format=duration), et l'inscrit dans le CSV. Il ne réécrit le fichier que si des modifications ont été détectées.

## Glossaire et données externalisées
Ajout d'un onglet "Glossaire" dans la navigation, généré automatiquement à partir de data/glossaire.md (converti en blocs dépliants <details> comme la documentation). Les titres et descriptions des mois (ex: "La saga de l'axe Z") ont été sortis du code Python de generer_site.py et déplacés dans data/mois.json. L'ajout d'un nouveau mois ou la modification d'un titre ne nécessite plus de toucher au script Python.

## Refonte du système de vote
Remplacement du système d'étoiles (qui affichait 5/5 par défaut, bloquant l'interaction des visiteurs) par un bouton unique "Utile". Le clic est enregistré comme un événement GoatCounter (path: '/vote-utile') visible dans l'onglet "Events" du tableau de bord. Le bouton se grise localement après le clic (localStorage) pour éviter les doublons.

## Compatibilité gestion_site.py
Mise à jour des fonctions _ligne_csv et ecrire_videos_csv dans l'interface graphique PySide6 pour prendre en charge les deux nouvelles colonnes sans casser l'ajout de vidéos existant. Le lecteur CSV ignore désormais silencieusement les clés None (piège Python 3.14 avec les virgules en fin de ligne).
# 28 juin 2026 — Interface graphique de gestion du site (gestion_site.py)

## Nouvelle interface graphique Qt6

Ajout d'une interface graphique (`gestion_site.py`, PySide6/Qt6) qui regroupe toutes les opérations de maintenance du site dans une seule fenêtre : tableau de bord (statistiques, répartition par phase, état Git), génération du site, ajout de vidéo (avec aperçu miniature et chaîne automatique archive → miniature → CSV → regen), génération de miniatures en lot, synchronisation Git (status / pull / commit + push) et édition des fichiers de données. Remplace l'ancien `goup_site.sh` absent. Console intégrée affichant les commandes et leur sortie en temps réel. Thème dark/orange cohérent avec le site, favicon intégré en barre latérale.

## Script d'installation multi-distribution

Ajout de `installer_dependances.sh` qui détecte la distribution (Arch/CachyOS/Manjaro, Debian/Ubuntu/Mint, Fedora) et installe automatiquement toutes les dépendances : Python, PySide6, pyserial, ffmpeg, git et les librairies runtime Qt (Wayland/X11). Si PySide6 n'est pas dans les dépôts, le script crée un virtualenv et un lanceur `lancer_gestion_site.sh`. Vérification finale des 5 dépendances.

## Licences

Le kit adopte un modèle à deux licences : **MIT** pour le code source (scripts Python et shell), **CC BY-SA 4.0** pour la documentation et les designs (Markdown, HTML, CSS, favicon, photos, textes). Le détail figure dans le fichier `LICENSE` et le `README.md` du kit.

![PrintNC - Orange Mécanique - Gestion du site](photos/GestionSite.png)

# 26 juin 2026 — Référence caméra de positionnement ajoutée à la BOM

## Caméra référencée (27 €)

Ajout de la référence d'achat de la caméra de positionnement (vue CAMVIEW) dans la BOM : caméra USB 2k Redeagle + objectif C-mount 5-50 mm, achetée 27 € sur AliExpress (https://fr.aliexpress.com/item/1005008742183752.html). La ligne caméra de la section « Électronique — Interface » passe de « — » à 27 € avec lien produit cliquable. Sous-total Interface : 118.98 € → 145.98 €. Total général : articles 3781.33 € → 3808.33 €, total final 4045.75 € → 4072.75 €.

# 24 juin 2026 — Bouton CAM VERS OUTIL (décalage caméra/broche)

## Bouton de décalage caméra ajouté

Bouton "CAM VERS OUTIL" qui amène la caméra à la place de la fraise par un déplacement relatif de l'offset caméra/broche, depuis n'importe quelle position. Workflow : poser la fraise sur le point visé → clic (la caméra vient au-dessus du point) → ajustement fin au jog en regardant l'image → REF CAMERA pour poser le zéro pièce. Le bouton et REF CAMERA lisent les mêmes champs (lineEdit_camera_x / camera_y), donc le décalage et la compensation sont cohérents par construction. Avant, la méthode consistait à mettre d'abord le XY à zéro, puis à se déplacer en absolu de l'offset (par exemple `G0 X-76 Y-85`) ; désormais, plus besoin de passer par X0 Y0 — le handler envoie simplement un saut relatif `G91 G0 X[-cam_x] Y[-cam_y]` puis `G90`, depuis la position courante, via deux CALL_MDI_WAIT.

## Bug : la fraise traversait la table au lieu du petit saut (RÉSOLU)

Symptôme déroutant : en MDI manuel, `G91 G0 X-76 Y-85` allait direct en 2 s ; lancé depuis le bouton, la fraise traversait toute la table vers l'origine. Le handler Python était pourtant correct (le status bar affichait bien la bonne commande).

Cause racine : le bouton avait été créé dans Qt Designer en RÉUTILISANT un bouton existant, qui gardait sa connexion d'origine dans le .ui vers le slot `btn_goto_location_clicked()` (lequel fait un `G53 G0 Z0` puis `G53 G0 X.. Y..` en coordonnées MACHINE). À chaque clic, DEUX actions partaient en parallèle : la connexion Python ajoutée à la main (bon déplacement relatif) ET la connexion parasite du .ui (G53 absolu machine → traversée vers l'origine). En MDI manuel ce parasite n'existe pas, d'où la différence.

Diagnostic par grep sur le .ui :

```
<sender>btn_camera_to_tool</sender>
<signal>clicked()</signal>
<slot>btn_goto_location_clicked()</slot>
```

Correction : suppression du bloc `<connection>` parasite dans le .ui. Le bouton ne garde que la connexion Python définie dans `initialized__` (`self.w.btn_camera_to_tool.clicked.connect(self.btn_camera_to_tool_clicked)`). Vérification : `grep btn_camera_to_tool` sur le .ui ne doit laisser que la définition du widget, plus aucune ligne `<sender>`.

Leçon : réutiliser un bouton dans Designer conserve ses connexions signal/slot du .ui, invisibles côté handler. Toujours vérifier (F4 dans Designer, ou grep sur le .ui) et supprimer l'ancienne connexion avant d'en câbler une nouvelle — ou tout gérer côté Python en laissant le bouton non connecté dans le .ui. Quand un widget réagit "en double" alors que le code semble correct, le diagnostic est dans le .ui, pas dans le handler. Le sous-programme externe cam_to_tool.ngc, d'abord envisagé, est abandonné : tout passe par le handler.

## Bouton "Afficher le bureau"

Ajout d'un bouton (objectName btn_bureau) qui masque toutes les fenêtres pour accéder au bureau, via `wmctrl -k on` lancé en subprocess.Popen depuis la méthode show_desktop du handler. Dépendance : paquet wmctrl (`sudo apt install wmctrl`) ; si absent, le handler logue un avertissement sans planter. Spécifique XFCE/X11. Connexion défensive dans initialized__ (hasattr) comme les autres boutons lanceurs (terminal, geany, navigateur, fichiers).

# 23 juin 2026 — Caméra de positionnement (vue CAMVIEW QtDragon)

## Caméra installée et fonctionnelle

Caméra USB "2k usb Camera Redeagle" (capteur HD 16:9) avec objectif C-mount varifocal 5-50 mm, utilisée pour le positionnement (touch off X/Y à la caméra). Vue intégrée dans l'onglet CAMVIEW de QtDragon (widget camview de qtvcp, basé sur OpenCV). Périphérique : /dev/video0 (vérifié avec `v4l2-ctl --list-devices` ; les /dev/video19-37 sont l'électronique interne du Pi 5, à ignorer). Outil v4l2-ctl installé via le paquet `v4l-utils`.

## Image ovale (rapport d'aspect) : corrigé par les échelles

L'image arrivait déformée (cercle = ovale vertical, aplati sur les côtés) : le capteur 16:9 était affiché dans un cadre carré. Réglages dans qtdragon.pref, section [CUSTOM_FORM_ENTRIES] :

```ini
Camview xscale = 165
Camview yscale = 100
Camview cam number = 0
Camview cam api = V4L2
Camview cam resolution = 1280,720
```

Points clés appris :

- Forcer une résolution 16:9 native (1280,720) au lieu de DEFAULT (OpenCV tombe sinon sur du 640x480 4:3). Modes natifs de la caméra listés avec `v4l2-ctl --list-formats-ext` : 2560x1440, 1920x1080, 1280x720 et 640x360 sont du 16:9.

- La ligne `Camview cam api = V4L2` était absente au départ ; sans elle l'API par défaut (ANY) ignorait la demande de résolution.

- Les échelles xscale/yscale sont en pourcentage. C'est le **xscale** (axe X) qu'il faut augmenter pour réétirer une image comprimée horizontalement, pas le yscale. Ajuster à l'œil sur une rondelle (~165).

- Édition à faire **LinuxCNC fermé** : QtDragon réécrit qtdragon.pref à la fermeture et écrase toute modif faite à chaud.

## Scintillement (bandes noires) sous éclairage LED 230V

Sous l'éclairage LED 230V/50Hz (papillotement à 100 Hz), des bandes noires défilantes apparaissent ; image nickel en lumière du jour. Pistes testées sur /dev/video0 :

- `power_line_frequency` était déjà sur 1 (50 Hz) : ce n'était pas le coupable.

- Exposition manuelle calée sur un multiple de 10 ms (100 Hz) : `auto_exposure=1` (Manual Mode, valeur contre-intuitive : 1=manuel, 3=auto) puis `exposure_time_absolute=100` (unités de 100 us, donc 100 = 10 ms). MAIS le firmware de la caméra **ignore l'exposition manuelle** (10 ou 100 donnent la même image) — piste abandonnée.

- Constat important : QtDragon/OpenCV reprend la main sur la caméra à l'ouverture du flux et écrase les réglages v4l2 poussés à la main. Tout réglage v4l2 doit être réappliqué APRÈS l'ouverture du flux.

- **Solution de fond retenue** : remplacer l'éclairage par une LED en courant continu (anneau USB 5V ou bandeau 12/24V sur l'alim continue de la machine), qui ne scintille pas du tout. À faire.

## Offset caméra / broche et touch off

L'offset entre l'axe de la caméra et l'axe de la broche se règle via les champs `Camera X` / `Camera Y` (onglet SETTINGS, ou section [CUSTOM_FORM_ENTRIES] de qtdragon.pref, LinuxCNC fermé). Mesure : graver un point avec la broche (noter X/Y machine), amener le réticule caméra sur ce même point (noter X/Y), l'offset = position caméra − position broche. Utilisation : amener le réticule sur le point d'origine voulu, puis bouton **REF CAMERA** (bloc OFFSETS, sous TOUCH PLATE) — QtDragon pose le G54 à l'aplomb de la broche en tenant compte de l'offset. Vérification de sécurité : après REF CAMERA, `G0 X0 Y0` en MDI à vide ; la broche doit tomber pile sur le point visé. Si décalé du déport → signe de l'offset à inverser. Le cercle et le réticule réglables (molette = zoom, clic droit = rotation) aident à centrer précisément.

## Support caméra déporté (à fabriquer)

Support pour fixer la caméra sur la face verticale droite du porte-broche (face 18x80 mm, 2 vis M6 entraxe 45 mm, vis à rallonger) avec un déport de ~12 mm vers la droite. Plaque ~48x73x12 mm : 2 trous M6 lamés côté face, poche de centrage 20x20 mm pour le pied de la caméra + trou central. Conçu via une macro FreeCAD paramétrique (support_camera.FCMacro). À imprimer en proto PLA/PETG puis usiner en alu (rigidité = stabilité de l'offset). Attention orientation : pour tourner la caméra de 180°, faire pivoter le corps caméra par rapport à son pied (la poche de centrage bloque le pied en rotation).

# 16 juin 2026 — VFD HuangYang en HYComm et refroidissement broche

## Lecture des paramètres du VFD via le protocole HYComm

Le VFD HuangYang 2.2 kW n'utilise pas le Modbus RTU standard mais son propre protocole série, le HYComm. Un script Modbus classique (minimalmodbus) reste muet : le VFD ne répond pas. Après analyse des trames échangées, le format de lecture d'un paramètre PD a été identifié :

```
Requete  : [adresse][0x01][0x03][numero_PD][0x00][0x00][CRC16]
Reponse  : [adresse][0x01][longueur][numero_PD][valeur...][CRC16]
```

La longueur vaut 0x03 (PD + 2 octets de valeur) ou 0x02 (PD + 1 octet). La validation se fait par le CRC16 et par l'écho du numéro de PD dans la réponse. Un script Python (lire_vfd.py) lit ainsi les paramètres PD000 à PD189 et les enregistre dans un fichier texte. Lecture seule, LinuxCNC doit être arrêté (le composant hy_vfd occupe sinon le port /dev/ttyAMA2). Outil publié sur GitHub : github.com/atelierduverdier/huanyang-vfd-reader.

## Paramètres VFD relevés et documentés

Valeurs principales lues sur la machine : fréquence max 400 Hz (PD005), tension max 220 V (PD008), moteur 220 V / 9 A / 2 pôles / 3000 tr/min à 50 Hz (PD141-144), communication adresse 1, 9600 bauds, 8N1 RTU (PD163-165). Documentés dans la section "Paramètres du VFD" du site.

## Accélération / décélération VFD portées à 3 s

PD014 (accélération) et PD015 (décélération) étaient à 1.5 s. Passés à 3 s pour ménager la broche : une décélération trop rapide renvoie de l'énergie sur le bus DC du VFD (risque de défaut surtension OU) et sollicite les roulements. 3 s élimine ce risque tout en restant confortable.

## Refroidissement broche : pompe (flood) + ventilateurs (AUX2) liés, avec post-refroidissement

La pompe à eau (sortie FLOOD / COOLANT, M8) et les ventilateurs (AUX2) sont désormais pilotés ensemble par un signal commun, avec maintien après l'arrêt de la broche pour évacuer la chaleur résiduelle.

Comportement :

- M3 (broche ON) ou M8 : pompe + ventilateurs démarrent immédiatement.

- M5 (broche OFF) ou M9 : pompe + ventilateurs restent actifs encore 30 s, puis s'arrêtent ensemble.

- Bouton AUX2 et M64 P2 / M65 P2 : commande manuelle des ventilateurs (inchangé).

Réalisation avec un composant timedelay (post-refroidissement) et deux or2 en cascade. Dans remora-flexi.hal :

```hal
loadrt or2 names=aux0_or,aux1_or,aux2_or,aux3_or,cool_or1,cool_or2
loadrt timedelay names=spindle_cooldown
addf cool_or1 servo-thread
addf cool_or2 servo-thread
addf spindle_cooldown servo-thread

setp spindle_cooldown.on-delay 0
setp spindle_cooldown.off-delay 30
net spindle-on => spindle_cooldown.in

# FLOOD = M8 OU post-refroidissement broche
net coolant-m8 iocontrol.0.coolant-flood => cool_or1.in0
net spindle-cooldown spindle_cooldown.out => cool_or1.in1
net cooling-active cool_or1.out => flexi.output.COOLANT
```

Dans custom_postgui.hal :

```hal
# AUX2 (ventilateurs) = (bouton OU M64) OU refroidissement actif
net aux2-or-out aux2_or.out => cool_or2.in0
net cooling-active => cool_or2.in1
net aux2-out cool_or2.out => flexi.output.AUX2
```

Le délai se règle avec setp spindle_cooldown.off-delay (en secondes). Piège rencontré : on ne peut pas relier deux fois le pin iocontrol.0.coolant-flood (déjà lié au signal flood) ; il faut réutiliser le signal existant, pas le pin.

## Correction affectation AUX2

Le tableau d'affectation indiquait AUX2 = pompe à eau. En réalité AUX2 = ventilateurs broche, et la pompe est sur la sortie FLOOD (COOLANT). Documents AFFECTATION_AUX.md et tableau corrigés.

# 13 juin 2026 — Télécommande RJ45 et bugs HAL CYCLE_START / HOLD

## Bug CYCLE_START : le programme redémarrait en boucle, Stop ne tenait pas

La logique utilisait flexi.input.CYCLE_START.not alors que cette entrée est active HAUTE (FALSE au repos, TRUE en appui). Le .not restait donc TRUE en permanence au repos, et combine a program-is-idle, relançait halui.program.run en boucle dès que la machine redevenait idle. Corrigé en retirant le .not et en supprimant l'ancien mecanisme de single-step automatique (qui n'était plus nécessaire et participait au bug) :

```hal
net cycle-start-button flexi.input.CYCLE_START => run_and.in0
net program-is-idle halui.program.is-idle => run_and.in1
net program-run run_and.out => halui.program.run
```

## Bug HOLD : program.pause bloqué en permanence, GO HOME impossible

Même type de bug sur le Hold : flexi.input.FEED_HOLD.not était utilise alors que FEED_HOLD est FALSE au repos (vérifié via halshow). Le .not restait donc TRUE au démarrage, déclenchant une seule fois le toggle et bloquant hold_toggle.on / halui.program.pause a TRUE de façon permanente. Conséquence inattendue : GO HOME refusait avec "Linear move on line 0 would exceed joint 0's negative limit" car la machine se croyait en pause. Corrigé en retirant le .not :

```hal
net hold_button flexi.input.FEED_HOLD => hold_button_toggle.in
```

Déblocage immediat effectué via Resume avant correction du fichier.

## Conflit de câblage : carte de boutons locale vs télécommande RJ45

La carte de boutons (CYC/ST, HOLD, HALT, DOOR avec LEDs témoins) était câblée en parallele de la télécommande RJ45 sur les mêmes entrées FlexiHAL. Résultat : niveaux logiques perturbés sur SYS/ST et HOLD. Solution retenue : déconnexion des sorties SYS/ST et HOLD de la carte de boutons, RJ45 seul conservé sur ces deux lignes. HALT reste fonctionnel sur la carte de boutons (vérifié au multimetre, diode de protection MOSFET 2N7000 RAS).
A faire si réutilisation future de la carte boutons sur ces 2 lignes : ajouter une logique de découplage (diodes OU or2 comme déjà fait pour les sorties AUX0-3) pour éviter le conflit entre les deux sources de signal.

# 8 juin 2026

## Environnement de développement PC + simulation

Mise en place d'un PC de développement (x86_64, Debian) en complément du Raspberry Pi de production, synchronisés par git. Config de simulation créée pour travailler l'interface sans le matériel : remora-flexi-sim.ini/.hal, postgui_call_list_sim.hal, qtdragon_hd_sim.hal, custom_postgui_sim.hal. Remplace le composant flexi (SPI) et le VFD série par des équivalents simulés. Lancement : `linuxcnc ~/linuxcnc/configs/flexi-hal/remora-flexi-sim.ini`. Affichage fenêtre : retirer l'option -f (fullscreen) de la ligne DISPLAY.

## Qt Designer sur PC (x86_64)

Paquet qttools5-dev-tools (binaire "designer"). Alias PC avec x86_64-linux-gnu au lieu de aarch64-linux-gnu sur le Pi.

## Boutons lanceurs d'applications

Ajout dans le handler de 4 fonctions lançant des applications externes sans bloquer l'interface (subprocess.Popen) : terminal (xfce4-terminal), geany, navigateur, explorateur de fichiers. Connexions défensives (hasattr).

## Timings d'impulsion harmonisés

Le moteur Y2 (JOINT_3) était règle a STEPLEN/STEPSPACE = 5000 (reste d'un test sur un bruit moteur dont la vraie cause était les DIP switches du driver). Harmonisé a 2500 sur tous les axes : son nettement meilleur.

## Vitesse X/Y portée a 8000 mm/min

Après avoir testé 10000 mm/min (166.67 mm/s) sans perte de pas, la vitesse a finalement été ramenée a 8000 mm/min (133.33 mm/s) pour le confort sonore et thermique des moteurs (perte de couple a haute vitesse rattrapée par les drivers en boucle fermee, accentuee par la temperature). Modifications dans [AXIS_X], [JOINT_0], [AXIS_Y], [JOINT_1], [JOINT_3], [DISPLAY] et [TRAJ]. Latence du Pi vérifiée avec latency-test : excellente (jitter servo ~28 us).

## Bug bouton GO HOME a haute vitesse (RÉSOLU)

A haute vitesse, en fin de déplacement GO HOME : message "EMC_TASK_PLAN_PAUSE cannot be executed". Le bouton utilise CALL_MDI_WAIT avec un delai = distance / vitesse + marge, qui ignore le temps d'accélération/décélération. Avec une marge de 1 s, le WAIT expirait avant la fin du mouvement. Correction dans qtdragon_hd_handler.py, fonction calc_mdi_move_wait_time :

```python
avant : def calc_mdi_move_wait_time(self, dest_x, dest_y, wait_buffer_secs=1)
apres : def calc_mdi_move_wait_time(self, dest_x, dest_y, wait_buffer_secs=4)
```

## Widget web (QtWebEngine) supprimé (RÉSOLU)

Au démarrage : erreurs "page_allocator Invalid argument (22)" + gel de la boucle (~0.18 s). Le widget QtWebEngine (page HTML de l'onglet SETUP, non utilisée) plante au démarrage. Widget web_view supprimé dans Qt Designer (onglets PDF et PROPERTIES conserves). Handler protégé par hasattr(self.w,'web_view') and hasattr(self.w,'layout_HTML').

## Message EMC_TASK_PLAN_PAUSE au démarrage (RÉSOLU)

Popup au déverrouillage E-stop, présent "depuis toujours". La carte lit ses entrées en logique active basse (FEED_HOLD = TRUE au repos), donc halui.program.pause était forcé a TRUE en permanence. Correction dans remora-flexi.hal :

```hal
avant : net hold_button flexi.input.FEED_HOLD     => hold_button_toggle.in
apres : net hold_button flexi.input.FEED_HOLD.not => hold_button_toggle.in
```

Sujet connexe non resolu : la télécommande 3 boutons RJ45 ne répond physiquement que sur HALT ; CYCLE_START et HOLD ne changent pas d'état (câblage/brochage a vérifier).

# 7 juin 2026

## Logique bouton OU G-code (or2)

Chaque sortie AUX est pilotee par un or2 : relais actif si le bouton OU le G-code le demandé.

```hal
loadrt or2 names=aux0_or,aux1_or,aux2_or,aux3_or
addf aux0_or servo-thread
net aux0-gcode motion.digital-out-00 => aux0_or.in0
```

Dans custom_postgui.hal (charge apres le GUI) :

```hal
net aux0-btn qtdragon.aux0 => aux0_or.in1
net aux0-out aux0_or.out => flexi.output.AUX0
```

Important : le prefixe reel des pins de boutons est "qtdragon" (et non "qtvcp"). Verifier avec halcmd show pin | grep -i aux.

## Creation des boutons dans QtDragon_hd

Ecran copie avec `qtvcp copy` (ne jamais modifier l'ecran système). Boutons : PushButton de la categorie "linuxcnc - hal", objectName aux0..aux3, checkable coche. Le PushButton HAL créé automatiquement la pin qtdragon.<objectName>.

## Incident : boutons perdus dans Designer

Erreur "Pin qtdragon.aux0 does not exist" apres manipulations. Procedure de secours : commenter les lignes aux?-btn du postgui pour démarrer, recreer les boutons, vérifier avec halcmd, decommenter. Lecon : faire fonctionner d'abord, faire joli ensuite. Une modif a la fois.

# 6 juin 2026

## Sorties auxiliaires (relais) FlexiHAL

Piloter les relais (lumiere, arrosage, aspiration) via les sorties AUX de la FlexiHAL, commandables depuis QtDragon et le G-code (M64/M65). Configuration HAL directe, sans inversion (modules câbles en active HIGH) :

```hal
net aux0-sig motion.digital-out-00 => flexi.output.AUX0
net aux1-sig motion.digital-out-01 => flexi.output.AUX1
net aux2-sig motion.digital-out-02 => flexi.output.AUX2
net aux3-sig motion.digital-out-03 => flexi.output.AUX3
```

Prerequis INI (sinon M64/M65 ignores silencieusement) :

```ini
[EMCMOT]
NUM_DIO = 4
```

## Câblage matériel valide

Alimentation ET signal pris sur le bornier AUX 2 fils. Par module : borne + du bornier vers DC+, pont court DC+ <-> IN sur le module, borne - vers DC-. Le rail AUX doit être alimente (jumper P17 = MAIN = 24V). Limites : 1000 mA combines pour les 4 AUX, bobine >= 150 Ohm.

## Journal de resolution

La cause racine d'un long debogage était un jumper P17 defectueux (pas de contact) : le rail AUX n'était pas alimente (borne + a 0V au lieu de 24V). Pistes ecartees avant : NUM_DIO absent de l'INI, jumpers de modules incoherents, tentative d'inversion HAL (composant not) abandonnee. La config HAL et le câblage étaient corrects ; seul defaut matériel : le jumper.

# 5 juin 2026 — Debug toolchange

## Recursion M6 cassant la preview

Le script toolchange.ngc appele par REMAP=M6 contenait lui-même un M6, creant une recursion infinie : la preview G-code de QtDragon ne se chargeait plus. Correction : suppression du M6 parasite.

## Utilisation de #<_selected_tool>

Le script utilisait #5400 (outil courant) au lieu de #<_selected_tool> (outil demandé par T_ M6). Au premier M6 sans outil en broche, #5400 = 0 et le script sortait sans palper. Corrigé.

## Gestion d'erreur incompatible avec la preview

Les blocs IF...M2...ENDIF cassaient la preview QtDragon. Supprimes : G38.2 declenche déjà automatiquement une erreur en cas d'echec de palpage, la vérification de #5070 était redondante.

## TOOLSET_X incohérent

[PROBE] TOOLSET_X = -25.0 ne correspondait pas a [VERSA_TOOLSETTER] X = -50.0. Corrigé a -50.0.

# Mai 2026 — Changement d'outil manuel avec palpage auto

## Mise en service

Un OpenATC (changement semi-automatique) avait été tente puis abandonne. Solution retenue : changement d'outil MANUEL avec palpage AUTOMATIQUE de la longueur d'outil au palpeur fixe (X-50 Y60). Script toolchange.ngc via REMAP=M6 : double palpage (rapide + lent), mode 0 (Z zero sur martyre auto) ou mode 1 (Z zero sur piece manuel), gestion du premier outil de référence via #1000 et #1002. Subroutines MDI associees : reset_ref, set_mode_martyre, set_mode_piece.

## Bonnes pratiques REMAP apprises

Ne jamais rappeler le code M qui a declenche le REMAP dans son propre script. Utiliser #<_selected_tool> et non #5400. Eviter les IF contenant M2/M30 (cassent la preview). G38.2 gere ses propres erreurs.
