# --- JEU DE PLATEFORME COMPLET AVEC 100 NIVEAUX, SCORE, SONS, ET INTERFACE PLEIN ÉCRAN ---

import pygame
import sys
import random
import string
import json
import os

pygame.init()

# --- CONSTANTES ---
LARGEUR, HAUTEUR = 800, 600
FPS = 60
GRAVITE = 0.5
SAUT_FORCE = -10

# --- COULEURS ---
BLEU_CIEL = (135, 206, 235)
NOIR = (0, 0, 0)
BLEU = (50, 50, 255)
VERT = (0, 200, 0)
ROUGE = (255, 50, 50)
BLANC = (255, 255, 255)
GRIS = (240, 240, 240)

# --- INIT PYGAME ---
screen = pygame.display.set_mode((LARGEUR, HAUTEUR), pygame.FULLSCREEN)
pygame.display.set_caption("Jeu Plateforme Ultime")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# --- SONS ---
try:
    son_saut = pygame.mixer.Sound("saut.wav")
    son_mort = pygame.mixer.Sound("mort.wav")
    son_victoire = pygame.mixer.Sound("victoire.wav")
    pygame.mixer.music.load("fond.mp3")
    pygame.mixer.music.play(-1)
except:
    son_saut = son_mort = son_victoire = None

# --- UTILISATEUR & SCORE ---
FICHIER_UTILISATEUR = "joueur.json"
def generer_code_ami():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def charger_donnees():
    if os.path.exists(FICHIER_UTILISATEUR):
        with open(FICHIER_UTILISATEUR, "r") as f:
            return json.load(f)
    else:
        return {"code": generer_code_ami(), "amis": [], "score": 0, "niveau": 0}

def sauvegarder_donnees(data):
    with open(FICHIER_UTILISATEUR, "w") as f:
        json.dump(data, f)

utilisateur = charger_donnees()

# --- GÉNÉRATION DE NIVEAUX ---
def generer_niveaux(nombre=100):
    niveaux = []
    for i in range(nombre):
        plateformes = [pygame.Rect(0, 550, 800, 50)]
        obstacles = []
        y = 500
        for j in range(1, 5 + i // 20):
            x = random.randint(50, 700)
            y -= random.randint(50, 100)
            plateformes.append(pygame.Rect(x, y, 100, 20))
            if random.random() < 0.5:
                obstacles.append(pygame.Rect(x + 25, y - 40, 50, 40))
        porte = pygame.Rect(plateformes[-1].x + 50, plateformes[-1].y - 50, 40, 50)
        niveaux.append({"plateformes": plateformes, "obstacles": obstacles, "porte": porte})
    return niveaux

niveaux = generer_niveaux(100)
niveau_actuel = utilisateur.get("niveau", 0)
score = utilisateur.get("score", 0)

# --- JOUEUR ---
joueur = pygame.Rect(100, 500, 50, 50)
vitesse_y = 0
au_sol = False
gagné = False
input_text = ""
info_message = ""

# --- FONCTIONS ---
def reset_joueur():
    joueur.x, joueur.y = 100, 500
    global vitesse_y
    vitesse_y = 0

def dessiner_pique(rect):
    pygame.draw.polygon(screen, ROUGE, [(rect.left, rect.bottom), (rect.centerx, rect.top), (rect.right, rect.bottom)])

def afficher_interface():
    pygame.draw.rect(screen, GRIS, (screen.get_width() - 250, 0, 250, HAUTEUR))
    screen.blit(font.render("Code ami:", True, NOIR), (screen.get_width() - 240, 10))
    screen.blit(font.render(utilisateur["code"], True, BLEU), (screen.get_width() - 240, 40))
    screen.blit(font.render("Entrer un code ami:", True, NOIR), (screen.get_width() - 240, 80))
    pygame.draw.rect(screen, BLANC, (screen.get_width() - 240, 110, 180, 30))
    pygame.draw.rect(screen, NOIR, (screen.get_width() - 240, 110, 180, 30), 1)
    screen.blit(font.render(input_text, True, NOIR), (screen.get_width() - 235, 115))
    screen.blit(font.render(info_message, True, VERT if "ajouté" in info_message else ROUGE), (screen.get_width() - 240, 150))
    screen.blit(font.render("Amis:", True, NOIR), (screen.get_width() - 240, 200))
    for i, ami in enumerate(utilisateur["amis"]):
        screen.blit(font.render(f"- {ami}", True, (0, 0, 255)), (screen.get_width() - 230, 230 + i * 25))
    screen.blit(font.render(f"Score: {score}", True, NOIR), (10, 10))
    screen.blit(font.render(f"Niveau: {niveau_actuel + 1}/100", True, NOIR), (10, 40))

# --- BOUCLE PRINCIPALE ---
while True:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sauvegarder_donnees(utilisateur)
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and not gagné:
            if event.key == pygame.K_RETURN:
                if input_text and input_text != utilisateur["code"] and input_text not in utilisateur["amis"]:
                    utilisateur["amis"].append(input_text)
                    info_message = f"Ami {input_text} ajouté !"
                elif input_text == utilisateur["code"]:
                    info_message = "Vous ne pouvez pas vous ajouter vous-même."
                elif input_text in utilisateur["amis"]:
                    info_message = "Cet ami est déjà dans la liste."
                else:
                    info_message = "Code invalide."
                input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 6 and event.unicode.isalnum():
                    input_text += event.unicode.upper()

    touches = pygame.key.get_pressed()
    if not gagné:
        if touches[pygame.K_LEFT]: joueur.x -= 5
        if touches[pygame.K_RIGHT]: joueur.x += 5
        if touches[pygame.K_SPACE] and au_sol:
            vitesse_y = SAUT_FORCE
            if son_saut: son_saut.play()
            au_sol = False

        vitesse_y += GRAVITE
        joueur.y += vitesse_y

        au_sol = False
        for p in niveaux[niveau_actuel]["plateformes"]:
            if joueur.colliderect(p) and vitesse_y >= 0:
                joueur.y = p.top - joueur.height
                vitesse_y = 0
                au_sol = True

        for obstacle in niveaux[niveau_actuel]["obstacles"]:
            if joueur.colliderect(obstacle):
                if son_mort: son_mort.play()
                info_message = "💥 Aïe !"
                reset_joueur()
                score = max(0, score - 10)

        if joueur.colliderect(niveaux[niveau_actuel]["porte"]):
            if son_victoire: son_victoire.play()
            score += 50
            niveau_actuel += 1
            if niveau_actuel >= len(niveaux):
                info_message = "🏁 Félicitations, vous avez terminé les 100 niveaux !"
                gagné = True
            else:
                reset_joueur()
            utilisateur["niveau"] = niveau_actuel
            utilisateur["score"] = score
            sauvegarder_donnees(utilisateur)

    screen.fill(BLEU_CIEL)
    for p in niveaux[niveau_actuel]["plateformes"]:
        pygame.draw.rect(screen, NOIR, p)
    for obs in niveaux[niveau_actuel]["obstacles"]:
        dessiner_pique(obs)
    pygame.draw.rect(screen, VERT, niveaux[niveau_actuel]["porte"], border_radius=6)
    pygame.draw.rect(screen, BLEU, joueur, border_radius=6)
    afficher_interface()
    if gagné:
        screen.blit(font.render("🎉 Jeu terminé ! Merci d'avoir joué !", True, VERT), (100, 100))
    pygame.display.flip()
