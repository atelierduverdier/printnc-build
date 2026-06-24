# 24 juin 2026 — Bouton CAM VERS OUTIL (décalage caméra/broche)

## Bouton de décalage caméra ajouté
Bouton "CAM VERS OUTIL" qui amène la caméra à la place de la fraise par un déplacement relatif de l'offset caméra/broche, depuis n'importe quelle position. Workflow : poser la fraise sur le point visé → clic (la caméra vient au-dessus du point) → ajustement fin au jog en regardant l'image → REF CAMERA pour poser le zéro pièce. Le bouton et REF CAMERA lisent les mêmes champs (lineEdit_camera_x / camera_y), donc le décalage et la compensation sont cohérents par construction. Plus besoin de passer par X0 Y0 comme avant. La méthode du handler envoie simplement `G91 G0 X[-cam_x] Y[-cam_y]` puis `G90`, via deux CALL_MDI_WAIT.

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

- Une échelle **négative** retourne l'image sur cet axe (utile pour un montage caméra à l'envers, ou pour une image en miroir par rapport au mouvement réel de la table).

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
