# Élysée 500 pour RaspyDarts

Créateur : **dodoche2638**. Version 3.7, conçue pour RaspyDarts 4.5.1.

Jeu de fléchettes pour **2 à 39 participants**, avec 39 personnages, un décor de l’Élysée, une carte et une intro animée de 25 secondes sur La Marseillaise.

## Télécharger et installer

Télécharger [le paquet complet](Elysee_500_RaspyDarts.zip), puis le décompresser sur le PC. Quitter RaspyDarts avant les transferts.

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

Trois numéros sont éclairés en bleu, blanc et rouge pour chaque manche. Sur ces numéros : simple = 1 point, double = 2, triple = 3. Pour chaque numéro, le meilleur score unique gagne un territoire ; une égalité laisse le territoire indécis.

Après trois manches, les deux meilleurs passent en finale. Classement des qualifications : territoires, points cumulés, puis ordre d’inscription.

En finale libre, on compare les points sur les trois numéros. Avec finition imposée, chaque touche conforme vaut un point. Les deux finalistes terminent leurs trois fléchettes. Égalité : nouvelle volée complète, scores de finale remis à zéro.

### Course aux 500 parrainages

Toute la cible compte à sa valeur normale, avec simple bull = 25 et double bull = 50. À partir de 500, tous les joueurs terminent le tour et le meilleur total gagne. En cas d’égalité en tête, seuls les ex æquo rejouent un tour complet, jusqu’au départage.

Avec finition imposée, chaque fléchette qui atteint ou dépasse 500 doit respecter cette finition ; sinon elle rapporte zéro. Exemple : 480 + T20 avec finition Double = toujours 480.

## Options

| Option | Fonction |
|---|---|
| `premier_a_500` | Activée : Course aux 500. Désactivée : Conquête. |
| `effectif` | 0 : joueurs inscrits au menu général. 2 à 39 : participants gérés en relais par le jeu. |
| `aleatoire` | Distribue les personnages au hasard, sans doublon. |
| `finition` | 0 Libre ; 1 Triple ; 2 Double numéroté ; 3 Simple bull ; 4 Double bull. |

Si le menu général limite le nombre de joueurs, inscrire deux sièges relais, puis régler `effectif` sur le nombre réel de participants. Suivre le nom affiché par le jeu. Les statistiques génériques de la borne ne connaissent que les sièges relais.

Les vidéos de coups spéciaux du thème et les envois d’impacts au DMD sont désactivés pour ce jeu. L’intro est conservée. Les LED de cible restent utilisées.

## Diagnostic

Les exceptions du module sont enregistrées dans `logs/Elysee_500_erreur.log` (copie de secours : `/tmp/Elysee_500_erreur.log`).

Un affichage « 0 - 0 joueurs » indique une déclaration manquante dans `NbOfPlayersPerGame`. Un échec FileZilla mentionnant « restarting at file position » indique une reprise à désactiver : renvoyer le fichier en choisissant Remplacer.

## Validation

Démarrage confirmé sur la borne de développement après correction des transferts. Tests locaux avec la classe de base fournie : initialisation, règles de fin de tour et égalités. Compatibilité à vérifier pour les autres versions de RaspyDarts.

Ce dépôt contient un jeu additionnel ; RaspyDarts doit être installé séparément. Les droits des composants et ressources tiers restent ceux de leurs titulaires respectifs.
