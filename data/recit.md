# Avant-propos

Ce document raconte la construction de ma fraiseuse CNC PrintNC, depuis le tout premier montage à blanc jusqu'à la machine pleinement fonctionnelle. Il a été reconstitué à partir de mon journal de bord quotidien publié sur Instagram (@atelierduverdier), où j'ai documenté presque chaque jour mes avancées, mes échecs et mes petites victoires. Plus qu'une notice technique, c'est l'histoire d'un projet mené avec patience et persévérance — deux mots qui reviennent souvent, et pour cause.

![PrintNC - Orange Mécanique](photos/printnc.jpg)

# Janvier 2026 — Le montage à blanc

Tout commence fin janvier. Avant de visser quoi que ce soit définitivement, je procède à un premier montage à blanc de la machine, juste pour voir si tout s'emboîte correctement. Sage décision : dès le 30 janvier, je note déjà « beaucoup de petits problèmes à régler, équerrage... » mais la PrintNC avance bien. Faire ce montage à blanc se révèle très utile — c'est un conseil que je retiendrai.

La devise des premiers jours est déjà posée : « J'avance doucement mais sûrement. »

![PrintNC - le commencement](photos/debut.jpg)
![PrintNC -Construction table CNC](photos/tablecnc.jpg)

# Février 2026 — L'axe Z, ce chantier sans fin

Le mois de février est largement consacré à l'axe Z, et il me donne du fil à retordre. Je dois usiner les plaques de l'axe Z sur mon autre machine — pas vraiment faite pour ça — et les cotes ne sont pas toujours au rendez-vous.

C'est une succession de tentatives : une plaque réalisée « non sans mal » avec des défauts rattrapés, un problème d'entraxe de 2,5 mm entre le porte-moteur et la vis, des réimpressions 3D, des tests sur bois avant de passer à l'aluminium. Le 13 février, je lâche un « j'espère que c'est la bonne cette fois !! » qui en dit long sur la persévérance nécessaire. Et le 14 février, enfin : « Je suis enfin parvenu à faire mon axe Z, non sans mal. »

![PrintNC - Usinage plaque Z](photos/usinage_plaque_z.jpg)

En parallèle, je m'attaque à l'esthétique et aux détails : démontage complet pour la peinture (sous-couche puis une belle couche orange), réalisation d'un gabarit de perçage imprimé en 3D pour fixer le porte-broche au bon endroit, et réglage du porte-broche en m'appuyant sur le wiki PrintNC.

Fin février, le matériel sérieux entre en scène. Je nettoie la broche G-Penny 2,2 kW refroidie à eau, je dégraisse les patins des rails linéaires HGW20, et je m'attaque à une étape cruciale : le câblage de la broche, avec la soudure du connecteur aviation GX20. Entre le câble blindé et les petites pins, il a fallu sortir la double paire de lunettes — « on ne rajeunit pas, mais la précision n'attend pas ! »

![PrintNC - Moi en train de souder](photos/moi.jpg)

# Mars 2026 — Le montage mécanique et le début de l'électrique

Mars marque le vrai assemblage. Montage avec des vis de 6 mm et rondelles frein, réglage de l'axe X, et surtout un principe de méthode : ne pas serrer définitivement les vis avant d'avoir réglé l'équerrage. La mise en butée pour l'équerrage, les réglages divers... c'est minutieux.
![PrintNC - Positionnement des rails](photos/rail.jpg)
![PrintNC - Prémontage](photos/premontage.jpg)
![PrintNC - Prémontage](photos/premontage2.jpg)
![PrintNC - Prémontage](photos/premontage3.jpg)
![PrintNC - Prémontage](photos/premontage4.jpg)

L'aluminium me résiste : après plusieurs tentatives et un certain énervement, je finis par renoncer à usiner certaines pièces en alu sur l'ancienne machine et je reviens à des platines imprimées en 3D. « Échec total de mes platines en aluminium, je remets mes platines en 3D. » Mais comme je le note moi-même : « Dans les échecs il y a toujours du bon. » L'embase en aluminium est même remplacée par un tube d'acier coupé, dans l'esprit costaud de la machine.

Le 11 mars est un beau jour : après avoir cherché longtemps un problème, tout devient enfin fluide sur les rails parallèles. Je partage d'ailleurs la méthode qui m'a débloqué. Puis je documente plein d'astuces : fixation des blocs et supports moteur, attention à la qualité de surface des impressions 3D, mise à niveau des quatre côtés de la machine.

Le 13 mars : « Partie mécanique finalisée. » Une étape majeure.

Aussitôt, le 14 mars, j'enchaîne sur le boîtier électrique : découpe des goulottes, première « connerie » assumée avec humour, positionnement des perçages à la CNC, et début du câblage. L'atelier n'est pas aussi rangé que dans les vidéos YouTube — « Moi c'est... Moi » — mais ça avance.

![PrintNC - Montage du boîtier électrique](photos/montage_boitier_electrique.jpg)

Le 30 mars, grande satisfaction : « Enfin mes moteurs tournent ! » Et le lendemain, les capteurs de fin de course fonctionnent. Ça sent la fin.

![PrintNC - Arrière Nema23](photos/arriere_nema23.jpg)

# Avril 2026 — Mise en route, et un coup dur

Le mois d'avril s'ouvre sur de belles réussites : boîtier électrique terminé, première mise en route de la broche, activation du RS485 pour contrôler la vitesse de broche. Je commence à explorer LinuxCNC avec le firmware remora-flexi et l'interface QtDragon HD sur Raspberry Pi 4.

Le 8 avril, c'est la « VICTOIRE » : les moteurs tournent enfin sous LinuxCNC (avec un remerciement à Jean-François). Je réalise une longue démo de QtDragon.

Puis viennent les détails sans fin du montage final : modification de l'axe Z pour y passer un capteur, réflexion sur les capteurs, fabrication de boîtiers de connectique imprimés en 3D pour les moteurs Nema 23, supports de chemins de câbles. « Quand on croit que l'on a terminé... il y a toujours une petite chose qu'on oublie. »

Le 23 avril : « Premier démarrage de la PrintNC ! » La machine fonctionne, avec une démo de mouvement à 6000 mm/min — même s'il reste un problème de câble USB-C à régler. Le liquide de refroidissement de la broche est mis en place, la broche est rodée et monte à 24 000 tr/min.

Mais le 28 avril, coup dur : « Mauvaise nouvelle, carte grillée. » Le lendemain, je trouve la cause — une extension qui a fait griller la carte FlexiHAL. Un moment difficile dans un projet de cette ampleur.

# Mai 2026 — La renaissance et les réglages fins

Mai commence avec la PrintNC déclarée « terminée », en attendant la nouvelle carte FlexiHAL. Je tente même un sauvetage de la carte grillée. Le 6 mai, la nouvelle carte arrive et le premier test est un usinage tout simple : un carré, pour vérifier que c'est bien carré. « Et ouiii c'est bien carré ! »

S'ensuit une longue période de réglages minutieux qui montre tout le sérieux du travail : passage à 3200 step, patins caoutchouc et TPU sous les tubes acier, fixation du plateau (56 trous, 56 taraudages, 56 vis !), préparation des planches martyres. Le premier petit usinage prudent — un simple positionnement de perçage — est vécu comme « fantastique ».

Le réglage de la broche devient une quête à part entière : perpendicularité, parallélisme, équerrage, plans de référence. Je refais les réglages plusieurs fois, j'imprime des pièces dédiées, je documente longuement mon raisonnement. « C'est en répétant les gestes que l'on s'améliore. » Et le résultat est là : précision au centième.

Le 15 mai est une date charnière : « Ma PrintNC est fonctionnelle. 4 mois de réalisation. Au poil ! » Les copeaux volent, le surfaçage du chêne en bois de bout est un plaisir, et après tant de travail, voir la machine en action est une vraie satisfaction. Détail qu'on oublie toujours : l'évacuation des poussières.

La fin du mois est consacrée à l'optimisation et aux fonctions avancées : réglage fin des drivers CL57T v4.1, un bond spectaculaire de vitesse (de 6500 à 20 000 mm/min en pointe), impression d'un sabot d'aspiration. Puis la reprise de LinuxCNC après des mois sans pratique — « j'ai tout oublié ! » — et l'apprentissage de ses subtilités par rapport à GRBL (les histoires de limites à décaler).

Le palpeur de hauteur d'outil devient le grand chantier logiciel : après des essais infructueux, le 26 mai mon système de changement d'outil avec palpeur fonctionne enfin. Mieux : le 27 mai, plus aucun zéro manuel — je pose les outils et le reste est automatique. Un fichier unique « pour les gouverner tous ».

# Juin 2026 — ATC, relais et interface

Début juin, je me laisse tenter par un changeur d'outil automatique (ATC), moi qui ne voulais pourtant pas m'y attaquer tout de suite. L'essai est instructif mais le verdict tombe le 3 juin : « Pas convaincu du système, pas assez costaud. » Je reviens donc à mon script de changement d'outil semi-automatique manuel avec palpage auto, en l'améliorant et en corrigeant ses bugs.

Les derniers jours sont consacrés à l'intégration d'accessoires et à l'interface : mise en service de relais pour piloter aspirateur, lumière et pompe, avec des boutons dédiés ajoutés directement dans QtDragon. Le 8 juin, je personnalise l'interface LinuxCNC pour y placer mes boutons.

![PrintNC -Relais](photos/relais3.jpg)

# Bilan

Quatre à cinq mois de travail, des dizaines de pièces imprimées et réimprimées, une carte grillée puis remplacée, d'innombrables réglages d'équerrage et de perpendicularité, et une montée en compétence continue sur la mécanique, l'électronique et le logiciel LinuxCNC.

Ce qui ressort de ce parcours, ce n'est pas la perfection du premier coup — c'est exactement l'inverse. C'est la capacité à recommencer une plaque d'axe Z autant de fois que nécessaire, à transformer un « gros fail » en leçon, et à avancer « doucement mais sûrement ». La PrintNC de l'Atelier du Verdier est le fruit de cette persévérance.

> « Après tant de travail pour réaliser cette CNC, c'est un plaisir de la voir en action. »

> Document reconstitué à partir du journal de bord Instagram @atelierduverdier. Les citations en italique et entre guillemets sont des extraits des légendes d'origine.
