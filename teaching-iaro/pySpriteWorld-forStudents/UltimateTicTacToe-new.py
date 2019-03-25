# -*- coding: utf-8 -*-

# Nicolas, 2015-11-18

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo

import random 
import numpy as np
import sys



    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def manhattan(x1,y1,x2,y2):
    return abs(x1-x2)+abs(y1-y2)

class Node:
    def __init__(self,x,y,dParcourue,dMan,parent=None):
        self.parent = parent
        self.dParcourue = dParcourue
        self.dMan = dMan
        self.x = x
        self.y = y

def ajouteFront(noeud,wallStates,xFiole,yFiole):
    l=[]
    if(((noeud.x+1,noeud.y) not in wallStates) and (noeud.x+1 >= 0) and (noeud.y >= 0) and (noeud.x+1 <= 19) and (noeud.y <= 19)):
        dMan = manhattan(noeud.x+1,noeud.y,xFiole,yFiole)
        l.append(Node(noeud.x+1,noeud.y,noeud.dParcourue,dMan,noeud))
    if(((noeud.x-1,noeud.y) not in wallStates) and (noeud.x-1 >= 0) and (noeud.y >= 0) and (noeud.x-1 <= 19) and (noeud.y <= 19)):
        dMan = manhattan(noeud.x-1,noeud.y,xFiole,yFiole)
        l.append(Node(noeud.x-1,noeud.y,noeud.dParcourue,dMan,noeud))
    if(((noeud.x,noeud.y+1) not in wallStates) and (noeud.x >= 0) and (noeud.y+1 >= 0) and (noeud.x <= 19) and (noeud.y+1 <= 19)):
        dMan = manhattan(noeud.x,noeud.y+1,xFiole,yFiole)
        l.append(Node(noeud.x,noeud.y+1,noeud.dParcourue,dMan,noeud))   
    if(((noeud.x,noeud.y-1) not in wallStates) and (noeud.x >= 0) and (noeud.y-1 >= 0) and (noeud.x <= 19) and (noeud.y-1 <= 19)):
        dMan = manhattan(noeud.x,noeud.y-1,xFiole,yFiole)
        l.append(Node(noeud.x,noeud.y-1,noeud.dParcourue,dMan,noeud))
    return l

def minMan(listNoeud):
    mini = listNoeud[0].dMan
    n = listNoeud[0]
    for i in listNoeud:
        if i.dMan < mini:
            n = i
            mini = i.dMan
    return n

def minParcourue(listNoeud,xFiole,yFiole):
    for i in listNoeud:
        if ((i.x == xFiole) and (i.y == yFiole)):
            n = i
    nNext = n.parent
    while nNext.parent != None:
        n = nNext
        nNext = n.parent
    return n

def minPar(listNoeud):
    mini = listNoeud[0].dParcourue
    n = listNoeud[0]
    for i in listNoeud:
        if i.dParcourue < mini:
            n = i
            mini = i.dParcourue
    return n
    
def bestRowCol(posPlayer,posFiole,wallStates):
    xPlayer = posPlayer[0]
    yPlayer = posPlayer[1]
    xFiole = posFiole[0]
    yFiole = posFiole[1]
    front = []
    res = []
    res.append(Node(xPlayer,yPlayer,0,manhattan(xPlayer,yPlayer,xFiole,yFiole)))
    for i in ajouteFront(res[0],wallStates,xFiole,yFiole):
        front.append(i)
    test = True
    while front != []:
        noeudMin = minPar(front)
        res.append(noeudMin)
        front.remove(noeudMin)
        for i in ajouteFront(noeudMin,wallStates,xFiole,yFiole):
            for j in front:
                if test:
                    if((i.x == j.x) and (i.y == j.y)):
                        if i.dParcourue < j.dParcourue:
                            front.append(i)
                            front.remove(j)
                        test = False
            for j in res:
                if test:
                    if((i.x == j.x) and (i.y == j.y)):
                        if i.dParcourue < j.dParcourue:
                            res.append(i)
                            res.remove(j)
                        test = False
            if test:
                front.append(i)
            test = True
    n = minParcourue(res,xFiole,yFiole)
    return n.x,n.y
    
    
    
def init(_boardname=None):
    carte = ['cluedo','match','match2','pathfindingWorld3','pathfindingWorld_multiPlayer','pathfindingWorld_MultiPlayer2','pathfindingWorld_MultiPlayer3','pathfindingWorld_MultiPlayer4','thirst','tictactoe','tictactoeBis']
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'tictactoeBis'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 10  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 50000 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    
    
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
       
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    #score = [0]*nbPlayers
    #fioles = {} # dictionnaire (x,y)->couleur pour les fioles
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    
    # on localise tous les objets ramassables
    #goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    #print ("Goal states:", goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    # et la zone de jeu pour le tic-tac-toe
    tictactoeStates = [(x,y) for x in range(3,16) for y in range(3,16)]
    #print ("Wall states:", wallStates)
    
    # les coordonnees des tiles dans la fiche
    tile_fiole_jaune = (19,1)
    tile_fiole_bleue = (20,1)
    
    # listes des objets fioles jaunes et bleues
    
    fiolesJaunes = [f for f in game.layers['ramassable'] if f.tileid==tile_fiole_jaune]
    fiolesBleues = [f for f in game.layers['ramassable'] if f.tileid==tile_fiole_bleue]   
    all_fioles = (fiolesJaunes,fiolesBleues) 
    fiole_a_ramasser = (0,0) # servira à repérer la prochaine fiole à prendre
    
    # renvoie la couleur d'une fiole
    # potentiellement utile
    
    def couleur(o):
        if o.tileid==tile_fiole_jaune:
            return 'j'
        elif o.tileid==tile_fiole_bleue:
            return 'b'
    
    
    #-------------------------------
    # Placement aleatoire d'une fioles de couleur 
    #-------------------------------
    
    def put_next_fiole(j,t):
        o = all_fioles[j][t]
    
        # et on met cette fiole qqpart au hasard
    
        x = random.randint(1,19)
        y = random.randint(1,19)
    
        while (x,y) in tictactoeStates or (x,y) in wallStates: # ... mais pas sur un mur
            x = random.randint(1,19)
            y = random.randint(1,19)
        o.set_rowcol(x,y)
        # on ajoute cette fiole dans le dictionnaire
        #fioles[(x,y)]=couleur(o)
    
        game.layers['ramassable'].add(o)
        game.mainiteration()
        return (x,y)
        
        
    
    
    
    #-------------------------------
    # Boucle principale de déplacements, un joueur apres l'autre
    #-------------------------------
    
    posPlayers = initStates

    tour = 0    
    j = 0 # le joueur 0 commence
    # on place la premiere fiole jaune      

    fiole_a_ramasser = put_next_fiole(0,tour)    


    for i in range(iterations):
        # bon ici on fait juste plusieurs random walker pour exemple...
        row,col = posPlayers[j]

        #x_inc,y_inc = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
        #next_row = row+x_inc
        #next_col = col+y_inc
        next_row,next_col = bestRowCol(posPlayers[j],fiole_a_ramasser,wallStates)
        # and ((next_row,next_col) not in posPlayers)
        if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=19 and next_col>=0 and next_col<=19:
            players[j].set_rowcol(next_row,next_col)
            print ("pos :", j, next_row,next_col)
            game.mainiteration()

            col=next_col
            row=next_row
            posPlayers[j]=(row,col)
        
        # si on trouve la fiole par un grand hasard...
        if (row,col)==fiole_a_ramasser:
            o = players[j].ramasse(game.layers) # on la ramasse
            game.mainiteration()
            print ("Objet de couleur ", couleur(o), " trouvé par le joueur ", j)
            
            # ici il faudrait aller la mettre a la position choisie
            # pour jouer a ultimate tic-tac-toe
            # et verifier que la position est legale etc.            
            
            
            
            # on active le joueur suivant
            # et on place la fiole suivante
            j = (j+1)%2     
            if j == 0:
                tour+=1
                 
            fiole_a_ramasser=put_next_fiole(j,tour)    
    
                
                #break
            
    
    pygame.quit()
    
        
    
   

if __name__ == '__main__':
    main()
    


