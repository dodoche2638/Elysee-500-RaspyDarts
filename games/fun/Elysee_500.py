"""Élysée 500 — Conquête."""
import random
import colorsys
from types import SimpleNamespace
import pygame
from include import cgame, cplayer

OPTIONS = {'theme': 'default', 'effectif': 0, 'aleatoire': True, 'premier_a_500': 'conquete', 'finition': 0, 'nb_manches': 5}
OPTION_CHOICES = {'premier_a_500': [('conquete', 'Conquête de territoires'), ('course500', 'Course aux 500 parrainages')], 'nb_manches': [(3, '3 manches'), (5, '5 manches'), (7, '7 manches')], 'finition': [(0, 'Libre'), (1, 'Triple'), (2, 'Double (1 à 20)'), (3, 'Simple bull (25)'), (4, 'Double bull (50)')],
                  'effectif': [(0, 'Joueurs inscrits au menu')] + [(i, str(i) + ' participants en relais') for i in range(2, 40)]}
FINITIONS = ('Libre', 'Triple', 'Double', 'Simple bull (25)', 'Double bull (50)')
CIBLES_FIN = ((), tuple(f'T{i}' for i in range(1,21)), tuple(f'D{i}' for i in range(1,21)), ('SB',), ('DB',))
LOGO = 'Elysee_500.png'
NB_DARTS = 3
HEADERS = ['Terr.']
GAME_RECORDS = {}
VERSION = '3.9'
NOMS = ['Nathalie Arthaud', 'François Asselineau', 'Gabriel Attal', 'Delphine Batho', 'Olivier Becht', 'Sébastien Bonnal', 'Karim Bouamrane', 'Juan Branco', 'Mélody Delmur', 'Emmanuel Dubuisson', 'Nicolas Dupont-Aignan', 'Sylvain Durif', 'Clara Egger', 'Raphaël Glucksmann', 'Philippe Herlin', 'Anasse Kazib', 'Selma Labib', 'Francis Lalanne', 'Marine Le Pen', 'Jean-François Legendre', 'David Lisnard', 'Mira Markovic', 'Benoît Mathieu', 'Jean-Luc Mélenchon', 'Antoine Mikolajczak', 'Manolo Mlekuz', 'Édouard Philippe', 'Florian Philippot', 'Gilles Platret', 'Natacha Polony', 'Bruno Retailleau', 'Rémi Revillon d’Apreval', 'Teddy Riner', 'Erwan Rohou', 'Fabien Roussel', 'François Ruffin', 'David Saforcada', 'Marine Tondelier', 'Éric Zemmour']
PALETTE = [(69,140,212),(229,102,112),(80,184,158),(229,166,83),(153,109,208),(213,125,181),(123,175,80),(98,117,202)]


PALETTE.extend(tuple(int(255*c) for c in colorsys.hsv_to_rgb((i*.618034)%1,.55,.96)) for i in range(8,39))


def check_players_allowed(nb_players):
    return 2 <= nb_players <= 39, VERSION, 39


class CPlayerExtended(cplayer.Player):
    pass


class Game(cgame.Game):
    def __init__(self, display, game, nb_players, options, config, logs, rpi, dmd, video_player, free_launch=False, game_is_ok_for_color=True):
        super().__init__(display, game, nb_players, options, config, logs, rpi, dmd, video_player, free_launch, game_is_ok_for_color)
        self.rpi = rpi
        self.nb_players = nb_players
        self.nb_darts = 3
        manches = int(options.get('nb_manches', 5))
        self.nb_manches = manches if manches in (3, 5, 7) else 5
        self.max_round = self.nb_manches + 1
        self.logo = LOGO
        self.headers = HEADERS
        self.game_records = {}
        effectif = int(options.get('effectif', 0))
        self.relais = 2 <= effectif <= 39
        total = effectif if self.relais else nb_players
        self.personnages = random.sample(range(39), total) if str(options.get('aleatoire', True)).lower() in ('true', '1', 'oui') else list(range(total))
        self.participants = [SimpleNamespace(ident=i, name=NOMS[n], score=0, darts_thrown=0)
                             for i,n in enumerate(self.personnages)]
        self.manche = 1
        self.actif = 0
        self.dernier_actif = 0
        if self.relais:
            self.max_round = (total*3 + 2 + nb_players-1)//nb_players
        self.course = str(options.get('premier_a_500', False)).lower() in ('true', '1', 'oui', 'course500')
        choix = str(options.get('finition', 0))
        self.finition = int(choix) if choix in ('1','2','3','4') else 0
        # Les égalités peuvent imposer plusieurs tours de finale.
        self.max_round = 2147483647
        self.tour = 0
        self.secteurs = []
        self.points = []
        self.territoires = [0] * total
        self.cumul = [0] * total
        self.course_joueurs = list(range(total))
        self.finalistes = []
        self.bilan = ''
        self.termine = False
        self.proprietaires = [None] * (3 * self.nb_manches)
        self.barrage = []
        self.qualifies = []
        self.places_barrage = 0
        self.resultat_archive = None
        self.cache_images = {}
        self.cadre = None
        # Rétablir le DMD standard du moteur ; aucune vidéo spéciale de coup.
        self.show_dmd = True

    def image(self, nom, taille, couleur=None):
        key = (nom, taille, couleur)
        if key not in self.cache_images:
            chemin = self.display.file_class.get_full_filename('Elysee_500/' + nom, 'images')
            surface = pygame.image.load(chemin).convert_alpha()
            if couleur:
                surface.fill((*couleur, 255), special_flags=pygame.BLEND_RGBA_MULT)
            self.cache_images[key] = pygame.transform.scale(surface, taille)
        return self.cache_images[key]

    def carte(self, screen):
        w,h = screen.get_size()
        groupes = (len(self.proprietaires) + 8) // 9
        largeur = max(1, int(w * .23 / groupes))
        hauteur = min(int(h * .27), int(largeur * 144 / 156))
        taille = (largeur, hauteur)
        for k, proprio in enumerate(self.proprietaires):
            couleur = PALETTE[proprio] if proprio is not None else (90, 104, 123)
            screen.blit(self.image('zone' + str(k % 9), taille, couleur),
                        (int(w * .025) + (k // 9) * largeur, int(h * .36)))
        font = pygame.font.Font(None, max(12, int(h * .026)))
        for groupe in range(groupes):
            debut = 3 * groupe + 1
            fin = min(self.nb_manches, debut + 2)
            texte = f'M. {debut}' if debut == fin else f'M. {debut}-{fin}'
            surf = font.render(texte, True, (246, 240, 223))
            screen.blit(surf, (int(w * .025) + groupe * largeur,
                              int(h * .36) + hauteur + 4))

    def play_intro(self):
        return None, self.play_intro_only_video()


    def pre_dart_check(self, players, actual_round, actual_player, player_launch):
        if self.relais:
            players, actual_round, actual_player = self.participants, self.manche, self.actif
        elif actual_round == 1 and player_launch == 1:
            # Conserver le prénom du joueur tout en identifiant son personnage.
            player = players[actual_player]
            if not getattr(player, 'elysee_nomme', False):
                player.name = f'{player.name} · {NOMS[self.personnages[actual_player]]}'
                player.elysee_nomme = True
        if self.barrage and actual_player not in self.barrage:
            return 4
        if actual_round != self.tour:
            self.tour = actual_round
            self.secteurs = random.sample(range(1, 21), 1 if self.barrage else 3)
            self.points = [[0, 0, 0] for _ in players]
        if self.course and actual_player not in self.course_joueurs:
            return 4
        if self.finalistes and actual_player not in self.finalistes:
            return 4
        if self.course or (self.finalistes and self.finition):
            cibles = CIBLES_FIN[self.finition]
            if self.course and self.cumul[actual_player] < 440:
                cibles = ()
            self.rpi.set_target_leds('|'.join(f'{c}#green' for c in cibles))
            return 0
        self.rpi.set_target_leds('|'.join(
            f'{ring}{n}#{color}' for n, color in zip(self.secteurs, ('blue','white','red'))
            for ring in 'SDT'))
        return 0

    def fin_volee(self, players, joueur):
        if self.termine:
            return 3
        if self.course:
            if joueur != self.course_joueurs[-1]:
                return 1
            meilleur = max(self.cumul[i] for i in self.course_joueurs)
            if meilleur < 500:
                return 1
            premiers = [i for i in self.course_joueurs if self.cumul[i] == meilleur]
            if len(premiers) > 1:
                self.course_joueurs = premiers
                self.bilan = 'Égalité : tour supplémentaire entre les ex æquo'
                self.display.message([self.bilan], 1800, None, 'middle', 'big')
                return 1
            gagnant = premiers[0]
            self.winner = players[gagnant].ident
            self.termine = True
            self.bilan = f'{players[gagnant].name} gagne avec {meilleur} parrainages !'
            self.rpi.set_target_leds('')
            self.display.message([self.bilan], 2500, None, 'middle', 'big')
            return 3
        if self.barrage:
            if joueur == self.barrage[-1]:
                self.resoudre_barrage()
            return 1
        if self.finalistes:
            if joueur != max(self.finalistes):
                return 1
            meilleur = max(sum(self.points[i]) for i in self.finalistes)
            premiers = [i for i in self.finalistes if sum(self.points[i]) == meilleur]
            if len(premiers) > 1:
                self.bilan = 'Égalité en finale : nouveau tour de trois fléchettes chacun'
                self.display.message([self.bilan], 1800, None, 'middle', 'big')
                return 1
            gagnant = premiers[0]
            self.winner = players[gagnant].ident
            self.bilan = 'Élu : ' + players[gagnant].name
            self.termine = True
            self.rpi.set_target_leds('')
            self.display.message([self.bilan], 1600, None, 'middle', 'big')
            return 3
        if joueur == len(players)-1:
            acquis = []
            for k, numero in enumerate(self.secteurs):
                maxi = max(ligne[k] for ligne in self.points)
                premiers = [i for i, ligne in enumerate(self.points) if ligne[k] == maxi]
                nom = 'indécis'
                if maxi and len(premiers) == 1:
                    i = premiers[0]
                    self.territoires[i] += 1
                    players[i].score = self.territoires[i]
                    nom = players[i].name
                self.proprietaires[(self.tour-1)*3+k] = premiers[0] if maxi and len(premiers)==1 else None
                self.carte(self.display.screen)
                self.display.update_screen()
                pygame.time.delay(180)
                acquis.append(f'{numero} : {nom}')
            self.bilan = '   /   '.join(acquis)
            self.display.message(acquis, 1800, None, 'middle', 'big')
            if self.tour == self.nb_manches:
                self.preparer_finale()
        return 1

    def ordre_actuel(self):
        if self.course:
            return list(self.course_joueurs)
        return sorted(self.barrage or self.finalistes or range(len(self.participants)))

    def preparer_finale(self):
        ordre = sorted(range(len(self.territoires)), key=lambda i: -self.territoires[i])
        seuil = self.territoires[ordre[1]]
        self.qualifies = [i for i in ordre if self.territoires[i] > seuil]
        egaux = [i for i in ordre if self.territoires[i] == seuil]
        places = 2 - len(self.qualifies)
        if len(egaux) == places:
            self.finalistes = sorted(self.qualifies + egaux)
        else:
            self.barrage = sorted(egaux)
            self.places_barrage = places
            self.bilan = 'Barrage : 3 fléchettes chacun sur un même numéro'

    def resoudre_barrage(self):
        ordre = sorted(self.barrage, key=lambda i: -sum(self.points[i]))
        seuil = sum(self.points[ordre[self.places_barrage - 1]])
        acquis = [i for i in ordre if sum(self.points[i]) > seuil]
        egaux = [i for i in ordre if sum(self.points[i]) == seuil]
        self.qualifies.extend(acquis)
        self.places_barrage -= len(acquis)
        if len(egaux) == self.places_barrage:
            self.finalistes = sorted(self.qualifies + egaux)
            self.barrage = []
            self.bilan = 'Les deux finalistes sont qualifiés !'
        else:
            self.barrage = sorted(egaux)
            self.bilan = 'Égalité au barrage : nouveau numéro, nouvelle volée'

    def archiver_resultats(self, joueurs):
        import json
        from pathlib import Path
        from datetime import datetime
        from uuid import uuid4
        resultat = {'version': VERSION, 'date': datetime.now().isoformat(),
                    'mode': 'course' if self.course else 'conquete',
                    'manches': self.nb_manches, 'finition': FINITIONS[self.finition],
                    'gagnant': self.gagnant_reel,
                    'participants': [{'id': i, 'nom': j.name,
                       'territoires': self.territoires[i], 'points': self.cumul[i],
                       'flechettes': j.darts_thrown} for i, j in enumerate(joueurs)]}
        dossier = Path(getattr(self.config, 'root_dir', Path.cwd())) / 'results' / 'Elysee_500'
        try:
            dossier.mkdir(parents=True, exist_ok=True)
            fichier = dossier / (datetime.now().strftime('%Y%m%d_%H%M%S_') + uuid4().hex[:8] + '.json')
            fichier.write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding='utf-8')
            self.resultat_archive = str(fichier)
        except OSError as erreur:
            self.logs.error(f'Élysée 500 : impossible de sauvegarder le résultat : {erreur}')

    def cloturer(self, joueurs_borne, index_borne):
        ordre_avant = self.ordre_actuel()
        phase_avant = (bool(self.barrage), bool(self.finalistes))
        joueurs = self.participants if self.relais else joueurs_borne
        joueur = self.actif if self.relais else index_borne
        code = self.fin_volee(joueurs, joueur)
        if code == 3:
            self.gagnant_reel = self.winner
            self.archiver_resultats(joueurs)
            if self.relais:
                # Le moteur connaît les sièges : identifier explicitement le gagnant
                # sur le siège de résultat, tout en conservant le classement réel en JSON.
                gagnant = self.participants[self.gagnant_reel]
                siege = joueurs_borne[index_borne]
                siege.name = gagnant.name
                siege.score = gagnant.score
                siege.darts_thrown = gagnant.darts_thrown
                self.winner = siege.ident
            return 3
        if self.relais:
            ordre = self.ordre_actuel()
            changement = phase_avant != (bool(self.barrage), bool(self.finalistes))
            if changement or joueur == ordre_avant[-1]:
                self.manche += 1
                self.actif = ordre[0]
            else:
                self.actif = ordre[ordre.index(joueur) + 1]
        return code

    def post_dart_check(self, hit, players, actual_round, actual_player, player_launch):
        borne, index_borne = players, actual_player
        if self.relais:
            players, actual_player = self.participants, self.actif
        ring, num = hit[:1].upper(), hit[1:]
        if self.course:
            gain = {'SB': 25, 'DB': 50}.get(hit.upper(), 0)
            if num.isdigit() and 1 <= int(num) <= 20:
                gain = int(num) * {'S': 1, 'D': 2, 'T': 3}.get(ring, 0)
            if self.cumul[actual_player] + gain >= 500 and self.finition and hit.upper() not in CIBLES_FIN[self.finition]:
                gain = 0
            self.cumul[actual_player] += gain
            player = players[actual_player]
            player.score = self.cumul[actual_player]
        elif self.finalistes and self.finition:
            if hit.upper() in CIBLES_FIN[self.finition]:
                self.points[actual_player][0] += 1
        elif num.isdigit() and int(num) in self.secteurs:
            gain = {'S':1, 'D':2, 'T':3}.get(ring, 0)
            self.points[actual_player][self.secteurs.index(int(num))] += gain
            if not self.barrage and not self.finalistes and self.tour <= self.nb_manches:
                self.cumul[actual_player] += gain
        players[actual_player].darts_thrown += 1
        code = self.cloturer(borne, index_borne) if player_launch == 3 else 0
        return self.init_handler(code)

    def miss_button(self, players, actual_player, actual_round, player_launch):
        return self.post_dart_check('MISS', players, actual_round, actual_player, player_launch)['return_code']

    def early_player_button(self, players, actual_player, actual_round):
        return self.cloturer(players, actual_player)

    def refresh_game_screen(self, players, actual_round, max_round, RemDarts, nb_darts,
                            logo, headers, actual_player, TxtOnLogo=False, Wait=False,
                            OnScreenButtons=None, showScores=True, end_of_game=False,
                            endOfSet=None, Set=None, MaxSet=None, **kwargs):
        if self.relais:
            players, actual_round, actual_player = self.participants, self.manche, self.actif
        screen = self.display.screen
        w, h = screen.get_size()
        screen.blit(self.image('palais', (w,h)), (0,0))
        if self.cadre is None or self.cadre.get_size() != (w,h):
            self.cadre = pygame.Surface((w,h), pygame.SRCALPHA)
            for rect in [(0,.015,1,.21),(.012,.24,.26,.36),(.285,.24,.70,.34),(.012,.59,.976,.40)]:
                x,y,r,b=rect
                pygame.draw.rect(self.cadre,(10,20,40,205),(int(x*w),int(y*h),int(r*w),int(b*h)))
        screen.blit(self.cadre,(0,0))
        self.carte(screen)

        def label(txt, x, y, taille, largeur=.9, color=(246,240,223)):
            font = pygame.font.Font(None, max(12, int(taille*h)))
            surf = font.render(str(txt), True, color)
            if surf.get_width() > w*largeur:
                surf = pygame.transform.smoothscale(surf, (int(w*largeur),
                    max(1, int(surf.get_height()*w*largeur/surf.get_width()))))
            screen.blit(surf, surf.get_rect(center=(int(x*w), int(y*h))))

        label('ÉLYSÉE 500', .5,.085,.115)
        phase = 'DUEL FINAL' if (not self.course and bool(self.finalistes)) else ('BARRAGE POUR LA FINALE' if self.barrage else f'CONQUÊTE   •   MANCHE {actual_round}/{self.nb_manches}')
        label("PREMIER À 500 PARRAINAGES" if self.course else phase,.5,.185,.055)
        label(f'{players[actual_player].name}    •    {RemDarts} fléchette(s)',.64,.275,.055)
        for k, (n, couleur) in enumerate(zip([] if self.course or (self.finalistes and self.finition) else self.secteurs, ((65,150,255),(245,245,235),(250,95,100)))):
            x = .40+.225*k
            label(n,x,.42,.16,.27,couleur)
            label(f'{self.points[actual_player][k]} pts',x,.52,.055,.27)
        if self.barrage:
            label('3 fléchettes sur ce numéro : simple 1 / double 2 / triple 3', .64, .56, .033, .68)
        if self.course:
            label(f"{self.cumul[actual_player]} / 500", .64,.43,.14)
        if self.finition and (self.course or self.finalistes):
            label('Finition : ' + FINITIONS[self.finition], .64, .53 if self.course else .43, .055)
        indices = self.finalistes if (not self.course and bool(self.finalistes)) else sorted(range(len(players)), key=lambda i: (-self.territoires[i], -self.cumul[i], i))
        page = 0 if (not self.course and bool(self.finalistes)) else indices.index(actual_player) // 8
        indices = list(indices)[page*8:page*8+8]
        if len(players)>8 and (self.course or not self.finalistes):
            label(f'Classement {page+1}/{(len(players)+7)//8}',.14,.264,.036,.21)
        for rang,i in enumerate(indices):
            score = (f'{sum(self.points[i])} pts' if (not self.course and bool(self.finalistes)) else
                     f'{self.territoires[i]} terr.  |  ' + ' / '.join(map(str,self.points[i])))
            if self.course:
                score = f"{self.cumul[i]} / 500"
            col, row = rang%2, rang//2
            portrait = self.image('candidat'+str(self.personnages[i]), (int(h*.058),int(h*.07)))
            screen.blit(portrait,(int(w*(.028+.48*col)),int(h*(.598+.075*row))))
            label(f'{page*8+rang+1}. {players[i].name}   {score}',.28+.48*col,.635+.075*row,.045,.39,PALETTE[i])
        label(self.bilan or ('Classement final après le dernier joueur du tour' if self.course else 'Simple 1   •   Double 2   •   Triple 3'),.5,.94,.043)
        self.display.update_screen()
        if end_of_game:
            return self.display.end_of_game_menu(logo, stat_button=False)
        return [{}]


# Diagnostic des appels du moteur, sans masquer les erreurs.
def _elysee_diagnostic(method):
    from functools import wraps
    @wraps(method)
    def traced(self, *args, **kwargs):
        import traceback
        from pathlib import Path
        from datetime import datetime
        try:
            return method(self, *args, **kwargs)
        except Exception:
            report = ('\n' + datetime.now().isoformat() + ' — Élysée 500 ' + VERSION
                      + ' — ' + method.__name__ + '\n' + traceback.format_exc())
            for destination in (Path.cwd() / 'logs' / 'Elysee_500_erreur.log',
                                Path('/tmp/Elysee_500_erreur.log')):
                try:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with destination.open('a', encoding='utf-8') as stream:
                        stream.write(report)
                except OSError:
                    pass
            raise
    return traced

for _method in ('__init__', 'play_intro', 'play_intro_only_video',
                'pre_dart_check', 'refresh_game_screen', 'post_dart_check',
                'early_player_button', 'miss_button'):
    setattr(Game, _method, _elysee_diagnostic(getattr(Game, _method)))

