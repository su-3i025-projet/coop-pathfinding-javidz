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
def manhattan(x1,y1,x2,y2): #renvoie la distance de manhattan entre (x1,y1) et (x2,y2)
    return abs(x1-x2)+abs(y1-y2)

class Node: #classe noeud utilisee pour representer les cases de la map
    def __init__(self,x,y,dParcourue,dMan,parent=None):
        self.parent = parent
        self.dParcourue = dParcourue
        self.dMan = dMan
        self.x = x
        self.y = y

def ajouteFront(noeud,wallStates,xFiole,yFiole): #ajoute les 4 cases alentours si elles ne sont pas des obstacles
    l=[]
    if(((noeud.x+1,noeud.y) not in wallStates) and (noeud.x+1 >= 0) and (noeud.y >= 0) and (noeud.x+1 <= 19) and (noeud.y <= 19)):
        dMan = manhattan(noeud.x+1,noeud.y,xFiole,yFiole)
        l.append(Node(noeud.x+1,noeud.y,noeud.dParcourue+1,dMan,noeud))
    if(((noeud.x-1,noeud.y) not in wallStates) and (noeud.x-1 >= 0) and (noeud.y >= 0) and (noeud.x-1 <= 19) and (noeud.y <= 19)):
        dMan = manhattan(noeud.x-1,noeud.y,xFiole,yFiole)
        l.append(Node(noeud.x-1,noeud.y,noeud.dParcourue+1,dMan,noeud))
    if(((noeud.x,noeud.y+1) not in wallStates) and (noeud.x >= 0) and (noeud.y+1 >= 0) and (noeud.x <= 19) and (noeud.y+1 <= 19)):
        dMan = manhattan(noeud.x,noeud.y+1,xFiole,yFiole)
        l.append(Node(noeud.x,noeud.y+1,noeud.dParcourue+1,dMan,noeud))   
    if(((noeud.x,noeud.y-1) not in wallStates) and (noeud.x >= 0) and (noeud.y-1 >= 0) and (noeud.x <= 19) and (noeud.y-1 <= 19)):
        dMan = manhattan(noeud.x,noeud.y-1,xFiole,yFiole)
        l.append(Node(noeud.x,noeud.y-1,noeud.dParcourue+1,dMan,noeud))
    return l


def minParcourue(listNoeud,xFiole,yFiole): #renvoie le noeud qui amene a la fiole le plus rapidement
    if listNoeud == []: #si la liste est vide on renvoie -1 car nous ne bougerons pas
        return -1
    n = None
    for i in listNoeud: #on cherche le noeud qui a comme coordonnees la fiole
        if ((i.x == xFiole) and (i.y == yFiole)):
            n = i
    if n == None: #si ce noeud n a pas de parent on renvoie -1 car nous ne bougerons pas
        return -1
    l = []
    l.append(n)
    if n.parent == None:
        return n
    nNext = n.parent
    while nNext.parent != None: #boucle pour atteindre la case adjacente a la position du joueur
        n = nNext
        l.append(n)
        nNext = n.parent
    return l

def minPar(listNoeud): #renvoie la noeud avec la distance parcourue la plus petite
    mini = listNoeud[0].dParcourue
    n = listNoeud[0]
    for i in listNoeud:
        if i.dParcourue < mini:
            n = i
            mini = i.dParcourue
    return n
    
def strategie2(posPlayer,posFiole,wallStates): #renvoie le chemin pour la strategie 2
    xPlayer = posPlayer[0]
    yPlayer = posPlayer[1]
    xFiole = posFiole[0]
    yFiole = posFiole[1]
    front = [] #les cases a explorer
    res = [] #les cases deja explorees
    res.append(Node(xPlayer,yPlayer,0,manhattan(xPlayer,yPlayer,xFiole,yFiole))) #on ajoute la case ou le joueur est dans la reserve
    for i in ajouteFront(res[0],wallStates,xFiole,yFiole): #on ajoute les 4 cases alentours du joueur
        front.append(i)
    test = True #permet de reduire les boucles avec j
    test2 = True #permet de savoir si on a deja ajoute la noeud dans la reserve ou le front
    while front != []: #tant que le front n est pas vide on cherche un meilleur chemin
        noeudMin = minPar(front) #on va explorer les cases autour de la case ayant la distance parcourue la plus petite depuis notre position de base
        res.append(noeudMin) #on rajoute la case qu on explore a la reserve
        front.remove(noeudMin) #et on l enleve du front
        for i in ajouteFront(noeudMin,wallStates,xFiole,yFiole): #on boucle sur au maximum les 4 cases autour
            test = True
            for j in front: #pour tous les noeuds du front on va tester si il existe deja la cases dedans
                if test:
                    if((i.x == j.x) and (i.y == j.y)): 
                        if i.dParcourue < j.dParcourue: #si la case existe deja dedans et que la distance parcourue pour y arriver est plus petite on la remplace
                            front.append(i)
                            front.remove(j)
                        test = False
                        test2 = False
            for j in res: #on boucle sur la reserve pour la meme raison
                if test:
                    if((i.x == j.x) and (i.y == j.y)):
                        if i.dParcourue < j.dParcourue:
                            res.append(i)
                            res.remove(j)
                        test = False
                        test2 = False
            if test2:
                front.append(i)
            test2 = True
    l = minParcourue(res,xFiole,yFiole)
    if l == -1: #si on a recu -1 on renvoie les coordonnees du joueur car nous ne bougeons pas
        return Node(xPlayer,yPlayer,0,manhattan(xPlayer,yPlayer,xFiole,yFiole))
    return l

def nearestGoal(posPlayer,wallStates,goalStates): #renvoie l indice de la fiole la plus proche du joueur
    xPlayer = posPlayer[0]
    yPlayer = posPlayer[1]
    dist = 10000 #distance de la fiole la plus proche
    x=-1 #on renverra la fiole la plus proche grace a cette variable
    for e in range(0,len(goalStates)):
        xFiole = goalStates[e][0]
        yFiole = goalStates[e][1]
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
        for k in res:
            if k.x == xFiole and k.y == yFiole:
                if k.dParcourue < dist: #on test si la fiole qu on vient de tester est plus proche
                    dist = k.dParcourue #si oui on met a jour la distance de la fiole la plus proche 
                    x = e #on met a jour la fiole la plus proche
    if x == -1:
        return 0
    return x



def ajouteFront3(noeud,wallStates,xFiole,yFiole): #ajoute les 4 cases alentours si elles ne sont pas des obstacles pour la strategie 3
    l=[]
    if(((noeud.x+1,noeud.y,noeud.dParcourue+1) not in wallStates) and ((noeud.x+1,noeud.y,-1) not in wallStates) and (noeud.x+1 >= 0) and (noeud.y >= 0) and (noeud.x+1 <= 19) and (noeud.y <= 19)): #on fait attention aux obstacles temporels
        dMan = manhattan(noeud.x+1,noeud.y,xFiole,yFiole)
        l.append(Node(noeud.x+1,noeud.y,noeud.dParcourue+1,dMan,noeud))
    if(((noeud.x-1,noeud.y,noeud.dParcourue+1) not in wallStates) and ((noeud.x-1,noeud.y,-1) not in wallStates) and (noeud.x-1 >= 0) and (noeud.y >= 0) and (noeud.x-1 <= 19) and (noeud.y <= 19)):
        dMan = manhattan(noeud.x-1,noeud.y,xFiole,yFiole)
        l.append(Node(noeud.x-1,noeud.y,noeud.dParcourue+1,dMan,noeud))
    if(((noeud.x,noeud.y+1,noeud.dParcourue+1) not in wallStates) and ((noeud.x,noeud.y+1,-1) not in wallStates) and (noeud.x >= 0) and (noeud.y+1 >= 0) and (noeud.x <= 19) and (noeud.y+1 <= 19)):
        dMan = manhattan(noeud.x,noeud.y+1,xFiole,yFiole)
        l.append(Node(noeud.x,noeud.y+1,noeud.dParcourue+1,dMan,noeud))   
    if(((noeud.x,noeud.y-1,noeud.dParcourue+1) not in wallStates) and ((noeud.x,noeud.y-1,-1) not in wallStates) and (noeud.x >= 0) and (noeud.y-1 >= 0) and (noeud.x <= 19) and (noeud.y-1 <= 19)):
        dMan = manhattan(noeud.x,noeud.y-1,xFiole,yFiole)
        l.append(Node(noeud.x,noeud.y-1,noeud.dParcourue+1,dMan,noeud))
    return l

def strategie3(posPlayer,posFiole,wallStates): #renvoie le chemin pour la strategie 3
    xPlayer = posPlayer[0]
    yPlayer = posPlayer[1]
    xFiole = posFiole[0]
    yFiole = posFiole[1]
    front = [] #les cases a explorer
    res = [] #les cases deja explorees
    res.append(Node(xPlayer,yPlayer,0,manhattan(xPlayer,yPlayer,xFiole,yFiole))) #on ajoute la case ou le joueur est dans la reserve
    for i in ajouteFront3(res[0],wallStates,xFiole,yFiole): #on ajoute les 4 cases alentours du joueur
        front.append(i)
    test = True #permet de reduire les boucles avec j
    test2 = True #permet de savoir si on a deja ajoute la noeud dans la reserve ou le front
    while front != []: #tant que le front n est pas vide on cherche un meilleur chemin
        noeudMin = minPar(front) #on va explorer les cases autour de la case ayant la distance parcourue la plus petite depuis notre position de base
        res.append(noeudMin) #on rajoute la case qu on explore a la reserve
        front.remove(noeudMin) #et on l enleve du front
        for i in ajouteFront3(noeudMin,wallStates,xFiole,yFiole): #on boucle sur au maximum les 4 cases autour
            test = True
            for j in front: #pour tous les noeuds du front on va tester si il existe deja la cases dedans
                if test:
                    if((i.x == j.x) and (i.y == j.y)): 
                        if i.dParcourue < j.dParcourue: #si la case existe deja dedans et que la distance parcourue pour y arriver est plus petite on la remplace
                            front.append(i)
                            front.remove(j)
                        test = False
                        test2 = False
            for j in res: #on boucle sur la reserve pour la meme raison
                if test:
                    if((i.x == j.x) and (i.y == j.y)):
                        if i.dParcourue < j.dParcourue:
                            res.append(i)
                            res.remove(j)
                        test = False
                        test2 = False
            if test2:
                front.append(i)
            test2 = True
    l = minParcourue(res,xFiole,yFiole)
    if l == -1: #si on a recu -1 on renvoie les coordonnees du joueur car nous ne bougeons pas
        return Node(xPlayer,yPlayer,0,manhattan(xPlayer,yPlayer,xFiole,yFiole))
    return l

def nearestGoal3(posPlayer,wallStates,goalStates): #renvoie l indice de la fiole la plus proche du joueur pour la strategie 3
    xPlayer = posPlayer[0]
    yPlayer = posPlayer[1]
    dist = 10000 #distance de la fiole la plus proche
    x=-1 #on renverra la fiole la plus proche grace a cette variable
    for e in range(0,len(goalStates)):
        xFiole = goalStates[e][0]
        yFiole = goalStates[e][1]
        front = []
        res = []
        res.append(Node(xPlayer,yPlayer,0,manhattan(xPlayer,yPlayer,xFiole,yFiole)))
        for i in ajouteFront3(res[0],wallStates,xFiole,yFiole):
            front.append(i)
        test = True
        while front != []:
            noeudMin = minPar(front)
            res.append(noeudMin)
            front.remove(noeudMin)
            for i in ajouteFront3(noeudMin,wallStates,xFiole,yFiole):
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
        for k in res:
            if k.x == xFiole and k.y == yFiole:
                if k.dParcourue < dist: #on test si la fiole qu on vient de tester est plus proche
                    dist = k.dParcourue #si oui on met a jour la distance de la fiole la plus proche 
                    x = e #on met a jour la fiole la plus proche
    return x

def lessOne(wallStates): #on enleve un temps a tous les obstacles temporels
    newS = []
    for (x,y,z) in wallStates:
        if z <= 0: #les -1 sont les obstacles intemporels donc on fait tres attention a ne pas passer d un obstacle 0 a -1
            newS.append((x,y,z))
        else:
            newS.append((x,y,z-1))
    return newS

game = Game()

def init(_boardname=None):
    carte = ['cluedo','match','match2','pathfindingWorld3','pathfindingWorld_multiPlayer','pathfindingWorld_MultiPlayer2','pathfindingWorld_MultiPlayer3','pathfindingWorld_MultiPlayer4','thirst','tictactoe','tictactoeBis']
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'match'
    name = carte[1]
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 50 # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():
    strategie = 2
    #for arg in sys.argv:
    iterations = 1000 # default
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
    score = [0]*nbPlayers
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    
    # on localise tous les objets ramassables
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print ("Goal states:", goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)
    
    #-------------------------------
    # Placement aleatoire des fioles de couleur 
    #-------------------------------
    
    for o in game.layers['ramassable']: # les rouges puis jaunes puis bleues
    # et on met la fiole qqpart au hasard
        x = random.randint(1,19)
        y = random.randint(1,19)
        while (x,y) in wallStates:
            x = random.randint(1,19)
            y = random.randint(1,19)
        o.set_rowcol(x,y)
        game.layers['ramassable'].add(o)
        game.mainiteration()                

    print(game.layers['ramassable'])
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]

    
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
        
    # bon ici on fait juste plusieurs random walker pour exemple...
    
    posPlayers = initStates
    pathPlayer = [] #chaque case de ce tableau va contenir le chemin a faire du joueur i vers une fiole
    wallStatesForJ = [] #tous les obstacles dont les autres joueurs
    goalStatesNonTarget = []
    for i in goalStates:
        goalStatesNonTarget.append(i)
    if strategie == 3 :
        for i in posPlayers:
            wallStatesForJ.append((i[0],i[1],0))
            pathPlayer.append([])
        for (x,y) in wallStates:
            wallStatesForJ.append((x,y,-1))
        for i in range(iterations): #on boucle sur le nombre d iterations choisi
            for j in range(nbPlayers): #a chaque iteration on fera jouer tous les joueurs
                row,col = posPlayers[j] #on prend les positions actuelles du joueur
                if pathPlayer[j] == []: #on regarde si il a encore un chemin a parcourir vers une fiole sinon on lui en donne un
                    goal = nearestGoal3(posPlayers[j],wallStatesForJ,goalStatesNonTarget) #on va chercher la fiole la plus proche
                    pathPlayer[j] = strategie3(posPlayers[j],goalStatesNonTarget[goal],wallStatesForJ) #on va chercher son chemin
                    del(goalStatesNonTarget[goal]) #on enleve la fiole des objets a ramasser pour ne pas avoir plusieurs joueurs qui vont vers la meme fiole
                    if isinstance(pathPlayer[j],list):
                        for k in pathPlayer[j]:
                            wallStatesForJ.append((k.x,k.y,k.dParcourue))
                    else:
                        wallStatesForJ.append((pathPlayer[j].x,pathPlayer[j].y,pathPlayer[j].dParcourue))
                if isinstance(pathPlayer[j],list):
                    taille = len(pathPlayer[j])
                    n = pathPlayer[j][taille-1]
                    pathPlayer[j].remove(n)
                else:
                    n = pathPlayer[j]
                    pathPlayer[j] = []
                if n.x>=0 and n.x<=19 and n.y>=0 and n.y<=19: #on effectue l iteration du joueur j vers la fiole
                    players[j].set_rowcol(n.x,n.y)
                    game.mainiteration()
                    wallStatesForJ.remove((row,col,0))
                    row=n.x
                    col=n.y
                    posPlayers[j]=(row,col)
            
      
                # si on a  trouvé un objet on le ramasse
                if (row,col) in goalStates:
                    o = players[j].ramasse(game.layers)
                    game.mainiteration()
                    #print ("Objet trouvé par le joueur ", j)
                    goalStates.remove((row,col)) # on enlève ce goalState de la liste
                    score[j]+=1
                
        
                    # et on remet un même objet à un autre endroit
                    x = random.randint(1,19)
                    y = random.randint(1,19)
                    while (x,y) in wallStates:
                        x = random.randint(1,19)
                        y = random.randint(1,19)
                    o.set_rowcol(x,y)
                    goalStates.append((x,y)) # on ajoute ce nouveau goalState
                    goalStatesNonTarget.append((x,y)) # on ajoute ce nouveau goalState
                    game.layers['ramassable'].add(o)
                    game.mainiteration()
            
            wallStatesForJ = lessOne(wallStatesForJ)


                        
    if strategie == 2 :
        for i in posPlayers:
            wallStatesForJ.append((i[0],i[1]))
            pathPlayer.append([])
        for i in wallStates: 
            wallStatesForJ.append(i)
            wallStatesForJ.append(i)
        for i in range(iterations): #on boucle sur le nombre d iterations choisi
            for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement
                row,col = posPlayers[j]
                if pathPlayer[j] == []: #on regarde si il a encore un chemin a parcourir vers une fiole sinon on lui en donne un
                    goal = nearestGoal(posPlayers[j],wallStatesForJ,goalStatesNonTarget) #on va chercher la fiole la plus proche
                    pathPlayer[j] = strategie2(posPlayers[j],goalStatesNonTarget[goal],wallStatesForJ) #on va chercher son chemin
                    del(goalStatesNonTarget[goal]) #on enleve la fiole des objets a ramasser pour ne pas avoir plusieurs joueurs qui vont vers la meme fiole
                    if isinstance(pathPlayer[j],list):
                        for k in pathPlayer[j]:
                            wallStatesForJ.append((k.x,k.y))
                    else:
                        wallStatesForJ.append((pathPlayer[j].x,pathPlayer[j].y))
                if isinstance(pathPlayer[j],list):
                    taille = len(pathPlayer[j])
                    n = pathPlayer[j][taille-1]
                    pathPlayer[j].remove(n)
                else:
                    n = pathPlayer[j]
                    pathPlayer[j] = []
                if n.x>=0 and n.x<=19 and n.y>=0 and n.y<=19: #on effectue l iteration du joueur j vers la fiole
                    players[j].set_rowcol(n.x,n.y)
                    game.mainiteration()
                    wallStatesForJ.remove((n.x,n.y))
                    row=n.x
                    col=n.y
                    posPlayers[j]=(row,col)
            
      
                # si on a  trouvé un objet on le ramasse
                if (row,col) in goalStates: 
                    o = players[j].ramasse(game.layers)
                    game.mainiteration()
                    #print ("Objet trouvé par le joueur ", j)
                    goalStates.remove((row,col)) # on enlève ce goalState de la liste
                    score[j]+=1
                
        
                    # et on remet un même objet à un autre endroit
                    x = random.randint(1,19)
                    y = random.randint(1,19)
                    while (x,y) in wallStates:
                        x = random.randint(1,19)
                        y = random.randint(1,19)
                    o.set_rowcol(x,y)
                    goalStates.append((x,y)) # on ajoute ce nouveau goalState
                    goalStatesNonTarget.append((x,y)) # on ajoute ce nouveau goalState
                    game.layers['ramassable'].add(o)
                    game.mainiteration()            
                    break
            
    
    print ("scores:", score)
    pygame.quit()
    
        
    
   

if __name__ == '__main__':
    main()
    


