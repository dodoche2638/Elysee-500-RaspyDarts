# Élysée 500 pour RaspyDarts

Créateur : **dodoche2638**. Version 3.9, conçue pour RaspyDarts 4.5.1.

Jeu de fléchettes pour **2 à 39 participants**, avec 39 personnages, un décor de l’Élysée, une carte et une intro animée de 25 secondes sur La Marseillaise.

## Télécharger et installer

Télécharger [le paquet complet 3.9](Elysee_500_RaspyDarts.zip). Le ZIP contient le même module 3.9 que le dépôt. Quitter RaspyDarts avant les transferts.

Pour une mise à jour depuis 3.8 : remplacer `games/fun/Elysee_500.py` ; pour les descriptifs et les options clarifiées, sauvegarder puis remplacer `include/cscreen.py` avec le fichier adapté à cette borne fourni dans le ZIP. Les ressources graphiques et l’intro ne changent pas.

- `games/fun/Elysee_500.py` : module du jeu, à placer à côté de Castle.py.
- `images/logos_menu/Elysee_500.png` : logo du menu Fun.
- `images/Elysee_500/` : décor, portraits et carte (conserver ce sous-dossier).
- `images/Elysee_500.png` : logo du jeu.
- `videos/intros/intro_Elysee_500.mp4` : intro de 25 secondes.

Dans FileZilla, choisir **Remplacer**, jamais **Reprendre**, pour mettre à jour les fichiers. Vérifier le succès des transferts puis relancer RaspyDarts.

### Déclaration dans le menu

Sur les versions utilisant `NbOfPlayersPerGame`, ajouter à ce dictionnaire dans `include/cconfig.py` :

```python
'Elysee_500': [2, 39, False],
```

Sauvegarder le fichier existant avant modification. Les fichiers complets `include/cconfig.py` et `include/cscreen.py` du ZIP proviennent d’une borne personnalisée : **ne pas les écraser directement sur une autre installation**. `cscreen.py` ajoute seulement les descriptifs et libellés de ce jeu ; leur absence n’empêche pas les règles du jeu de fonctionner.

## Modes de jeu

Chaque participant lance trois fléchettes par tour.

### Conquête

Un territoire est une récompense à gagner sur **un numéro éclairé**.

Exemple : la manche propose **12 en bleu, 8 en blanc et 20 en rouge**. Chaque joueur lance **trois fléchettes au total**, à répartir comme il veut entre ces numéros.

| Touche | Points sur le territoire correspondant |
|---|---:|
| Simple du numéro éclairé | 1 |
| Double du numéro éclairé | 2 |
| Triple du numéro éclairé | 3 |
| Autre numéro, bull ou raté | 0 |

Les touches sur un même numéro s’additionnent. **Quand tous les joueurs ont terminé**, le meilleur score sur chaque numéro gagne le territoire correspondant. En cas d’égalité en tête, personne ne gagne ce territoire : il reste gris. Un joueur peut gagner plusieurs territoires dans la même manche.

**Exemple sur le 12 :** un double et un simple donnent 3 points. Si un adversaire fait un triple, il a aussi 3 points : à égalité en tête, le territoire reste indécis.

#### Comprendre l’écran

- **Les trois grands numéros** : où viser pendant cette manche.
- **Les points sous chaque numéro** : les points du joueur actif sur ce territoire.
- **« Terr. »** : le nombre de territoires gagnés.
- **La carte** : les territoires déjà attribués aux manches précédentes, dans la couleur de leur gagnant. Le bleu, blanc et rouge des cibles ne désignent pas les propriétaires.

Il y a **3 territoires à gagner par manche**, donc **9, 15 ou 21 au maximum sur 3, 5 ou 7 manches** (5 manches par défaut). Les deux joueurs ayant le plus de territoires vont en finale. À égalité de territoires pour une place en finale, les joueurs concernés disputent un barrage : trois fléchettes chacun sur un même numéro tiré au sort (simple 1, double 2, triple 3). Les places acquises sont conservées. Si nécessaire, les joueurs encore à égalité rejouent sur un nouveau numéro. Les points cumulés et l’ordre d’inscription ne décident pas de l’accès à la finale.

En finale libre, on compare les points sur trois nouveaux numéros. Avec finition imposée, chaque touche conforme vaut un point. Les deux finalistes terminent leurs trois fléchettes. À égalité, nouvelle volée complète, scores de finale remis à zéro.

### Course aux 500 parrainages

Toute la cible compte à sa valeur normale, avec simple bull = 25 et double bull = 50. À partir de 500, tous les joueurs terminent le tour et le meilleur total gagne. En cas d’égalité en tête, seuls les ex æquo rejouent un tour complet, jusqu’au départage.

Avec finition imposée, chaque fléchette qui atteint ou dépasse 500 doit respecter cette finition ; sinon elle rapporte zéro. Exemple : 480 + T20 avec finition Double = toujours 480.

## Options

| Option | Fonction |
|---|---|
| Mode de jeu (`premier_a_500`) | Conquête de territoires ou Course aux 500 parrainages. Les anciens booléens restent reconnus. |
| Manches (`nb_manches`) | 3, 5 ou 7. 5 par défaut. Utilisée seulement en Conquête. |
| `effectif` | 0 : joueurs inscrits au menu général. 2 à 39 : participants gérés en relais par le jeu. |
| `aleatoire` | Distribue les personnages au hasard, sans doublon. |
| `finition` | 0 Libre ; 1 Triple ; 2 Double numéroté ; 3 Simple bull ; 4 Double bull. |

Si le menu général limite le nombre de joueurs, inscrire deux sièges relais, puis régler `effectif` sur le nombre réel de participants. Suivre le nom affiché par le jeu. Les statistiques génériques de la borne ne connaissent que les sièges relais.

Le DMD standard de RaspyDarts est réactivé en 3.8 (`show_dmd = True`). Les vidéos de coups spéciaux du thème restent désactivées pour ce jeu. L’intro est conservée. Les LED de cible restent utilisées.

## Diagnostic

Les exceptions du module sont enregistrées dans `logs/Elysee_500_erreur.log` (copie de secours : `/tmp/Elysee_500_erreur.log`).

Un affichage « 0 - 0 joueurs » indique une déclaration manquante dans `NbOfPlayersPerGame`. Un échec FileZilla mentionnant « restarting at file position » indique une reprise à désactiver : renvoyer le fichier en choisissant Remplacer.

## Résultats en mode relais

La fin de partie utilise désormais le code 3 : le siège de résultat est identifié par le vrai nom du gagnant et son score, pour l’annonce native de victoire. Les statistiques génériques de RaspyDarts restent celles des sièges relais : elles ne constituent pas le classement de tous les participants.

Le résultat réel complet est sauvegardé dans `results/Elysee_500/*.json` : nom, points, territoires et fléchettes de chaque participant, avec l’identifiant du gagnant. Une erreur d’écriture est signalée dans les logs sans bloquer la fin de partie.

## Validation

Le DMD 3.8 a été testé et validé sur la borne par son utilisateur ; son fonctionnement est conservé. La version 3.9 a été vérifiée localement avec le cgame fourni, joueurs et matériel simulés : 3/5/7 manches, barrages successifs pour une ou deux places, finale à égalité, course à 500, relais et direct, code 3 et archive complète. Rendu Pygame 1280 × 720 vérifié. Le test physique de la 3.9 reste nécessaire.

Ce dépôt contient un jeu additionnel ; RaspyDarts doit être installé séparément. Les droits des composants et ressources tiers restent ceux de leurs titulaires respectifs.

