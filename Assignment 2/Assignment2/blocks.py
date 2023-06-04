# -*-coding: utf-8 -*
"""NAMES OF THE AUTHOR(S): Gaël Aglin <gael.aglin@uclouvain.be>"""
from search import *
import time

goal_state = None


#################
# Problem class #
#################
class Blocks(Problem):

    x = 5

    def successor(self, state):
        last_col = state.nbc  # last colonne
        last_row = state.nbr
        next_state = []

        for position, letter in state.dico.items():
            x = position[0]  # vertical
            y = position[1]  # horizontal
            if letter == '@':  # good position
                continue

            if deadlock_height(letter, x, state):
                return []

            if y - 1 >= 0 and state.grid[x][y - 1] == ' ':  # left possible
                new_grid = list(map(list, state.grid))
                x_left, y_left = checkFalling(x, y - 1, last_row, new_grid)
                new_grid[x_left][y_left] = letter  # new position
                if letter == (goal_state.grid[x_left][y_left]).lower():
                    new_grid[x_left][y_left] = '@'
                new_grid[x][y] = ' '  # last position
                new_grid = updateFalling(x, y, new_grid)  # update falling others
                new_state = State(new_grid)  # new state
                next_state.append((None, new_state))  # append in the list

            if y + 1 < last_col and state.grid[x][y + 1] == ' ':  # right possible
                new_R_grid = list(map(list, state.grid))

                x_right, y_right, = checkFalling(x, y + 1, last_row, new_R_grid)

                new_R_grid[x_right][y_right] = letter

                if letter == (goal_state.grid[x_right][y_right]).lower():
                    new_R_grid[x_right][y_right] = '@'

                new_R_grid[x][y] = ' '

                new_R_grid = updateFalling(x, y, new_R_grid)
                new_R_state = State(new_R_grid)

                next_state.append((None, new_R_state))

        return next_state

    def goal_test(self, state):
        count = 0
        for position, letter in state.dico.items():
            if letter == '@':
                count += 1

        return count == len(goal_state.dico)


###############
# State class #
###############
class State:
    def __init__(self, grid):
        self.nbr = len(grid)
        self.nbc = len(grid[0])
        self.grid = grid
        self.dico = dict()

        for i in range(self.nbr):
            for j in range(self.nbc):
                if grid[i][j] not in (' ', '#'):
                    self.dico.update({(i, j): grid[i][j]})

    def __str__(self):
        n_sharp = self.nbc + 2
        s = ("#" * n_sharp) + "\n"
        for i in range(self.nbr):
            s += "#"
            for j in range(self.nbc):
                s = s + str(self.grid[i][j])
            s += "#"
            if i < self.nbr - 1:
                s += '\n'
        return s + "\n" + "#" * n_sharp

    def __eq__(self, other):
        return self.grid == other.grid

    def __hash__(self):
        return hash(frozenset(self.dico.items()))


######################
# Auxiliary function #
######################
def readInstanceFile(filename):
    grid_init, grid_goal = map(lambda x: [[c for c in l.rstrip('\n')[1:-1]] for l in open(filename + x)],
                               [".init", ".goalinfo"])
    return grid_init[1:-1], grid_goal[1:-1]


def checkFalling(x, y, last_row, grid):
    """
    Function for gravity of a block
    """
    for x in range(x, last_row):  # fall until border
        if grid[x][y] not in ' ':  # fall until blocs
            return x - 1, y
    return x, y


def updateFalling(x, y, grid):
    """
    When move a block, blocks above fall
    """
    for x in range(x, 0, -1):  # au dessus de nous
        if grid[x - 1][y] not in (' ', '@', '#') and grid[x][y] not in '#':  # y a une lettre à faire tomber
            grid[x][y] = grid[x - 1][y]  # nouvelle valeur : on descend

            if grid[x][y] == (goal_state.grid[x][y]).lower() and grid[x][y] != " ":  # si nouvelle valeur est au bon
                # endroit
                grid[x][y] = '@'
            grid[x - 1][y] = ' '  # ancienne valeur
    return grid


def deadlock_height(letter, x, state):
    """ Verifie si la lettre est pas tombée trop bas pour atteindre le goal state"""
    heights = []
    # for x_goal in range(goal_state.nbr):
    #     for y_goal in range(goal_state.nbc):
    #         if goal_state.grid[x_goal][y_goal] == letter.upper():
    #             heights.append(x_goal)
    for key in goal_state.dico:
        if goal_state.dico[key] == letter.upper():
            heights.append(key[0])

    if not heights:
        return False
    lower_letter = sum(value == letter for value in state.dico.values())
    upper_letter = sum(value == letter.upper() for value in goal_state.dico.values())

    pos_at = []
    for pos, char in state.dico.items():
        if char == "@":
            pos_at.append(pos)
    count_bis = 0
    for at in pos_at:
        for gPos, gLetter in goal_state.dico.items():
            if gPos == at and gLetter == letter.upper():
                count_bis += 1

    count = upper_letter - lower_letter - count_bis
    for height in heights:
        if x > height:
            count += 1
    if count == len(heights):
        return True

    return False


# def deadlock_obstacle(letter, x, y, state):
#     """ Vérifie si le goal state est atteignable d'un point de vue horizontal et que c'est le dernier en x"""
#     # On cherche la position de tous les goal states
#     all_goal_pos = []
#     for x_goal in range(goal_state.nbr):
#         for y_goal in range(goal_state.nbc):
#             if goal_state.grid[x_goal][y_goal] == letter.upper():
#                 all_goal_pos.append([x_goal, y_goal])
#     # On cherche le x du goal state le plus bas
#     max_x = 0
#     for goal_pos in all_goal_pos:
#         if goal_pos[0] > max_x:
#             max_x = goal_pos[0]
#     # On garde tous les y des goal states se trouvant à la valeur max_x
#     same_x_goal = []
#     for goal_pos in all_goal_pos:
#         if goal_pos[0] == max_x:
#             same_x_goal.append(goal_pos[1])
#     # On cherche la position des murs à la même hauteur que la lettre concernée
#     all_wall_y = []
#     if x == max_x:
#         for i in range(state.nbc):
#             if state.grid[x][i] == "#":
#                 all_wall_y.append(i)
#     # Si jamais la lettre est à la même hauteur que le goal state le plus bas et qu'il y a un mur entre tous les goal
#     # states et la lettre, on revoit True
#     count = 0
#     if x == max_x:
#         for pos_goal in same_x_goal:
#             for wall_y in all_wall_y:
#                 if y < wall_y < pos_goal:
#                     count += 1
#                 if y > wall_y > pos_goal:
#                     count += 1
#     if count == len(same_x_goal):
#         print("pos: " + str(x) + " " + str(y))
#         return True
#     return False


######################
# Heuristic function #
######################
def heuristic(node):
    h = 0.0

    for final_position, final_letter in goal_state.dico.items():
        for position, letter in node.state.dico.items():
            if final_letter.lower() == letter:
                h += abs(final_position[1] - position[1])

    return h


##############################
# Launch the search in local #
##############################
# Use this block to test your code in local
# Comment it and uncomment the next one if you want to submit your code on INGInious
instances_path = "instances/"
instance_names = ['a01', 'a02', 'a03', 'a04', 'a05', 'a06', 'a07', 'a08', 'a09', 'a10']  # ,'a11']
# instance_names = ['a01', 'a02', 'a03', 'a04', 'a06', 'a07', 'a08', 'a09', 'a10']
# instance_names = ['a03'] #,'a04','a05','a06','a07','a08','a09','a10','a11']
# instance_names = ['a01', 'a02', 'a03']
# instance_names = ['a06']
for instance in [instances_path + name for name in instance_names]:
    grid_init, grid_goal = readInstanceFile(instance)
    init_state = State(grid_init)
    goal_state = State(grid_goal)

    # print(init_state)
    # print(goal_state)
    problem = Blocks(init_state)

    # example of bfs tree search
    startTime = time.perf_counter()
    # node, nb_explored, remaining_nodes = breadth_first_graph_search(problem)
    node, nb_explored, remaining_nodes = astar_graph_search(problem, heuristic)
    endTime = time.perf_counter()

    # example of print
    path = node.path()
    path.reverse()
    print("---------------------------")
    print(instance)
    print('Number of moves: ' + str(node.depth))
    # for n in path:
    #     print(n.state)  # assuming that the __str__ function of state outputs the correct format
    #     print()
    print("* Execution time:\t", str(endTime - startTime))
    print("* Path cost to goal:\t", node.depth, "moves")
    print("* #Nodes explored:\t", nb_explored)
    print("* Queue size at goal:\t", remaining_nodes)

####################################
# Launch the search for INGInious  #
####################################
# Use this block to test your code on INGInious
# instance = sys.argv[1]
# grid_init, grid_goal = readInstanceFile(instance)
# init_state = State(grid_init)
# goal_state = State(grid_goal)
# problem = Blocks(init_state)
#
# # example of bfs graph search
# startTime = time.perf_counter()
# node, nb_explored, remaining_nodes = astar_graph_search(problem, heuristic)
# endTime = time.perf_counter()
#
# # example of print
# path = node.path()
# path.reverse()
#
# print('Number of moves: ' + str(node.depth))
# for n in path:
#     print(n.state)  # assuming that the __str__ function of state outputs the correct format
#     print()
# print("* Execution time:\t", str(endTime - startTime))
# print("* Path cost to goal:\t", node.depth, "moves")
# print("* #Nodes explored:\t", nb_explored)
# print("* Queue size at goal:\t",  remaining_nodes)
