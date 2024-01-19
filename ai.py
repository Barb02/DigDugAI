# Students:
# Bárbara Nóbrega Galiza - 105937
# Pedro Daniel Fidalgo de Pinho - 109986

"""
Project evaluated in :
- Performance
- Quality of Architecture and Implementation
- Originality

The work aims in using three main chapters of AI 
- Agent Architectures
- Search Techniques
- Automated Problem Solving

Points are attributed based on :
- Type
- Position
- Kill weapon
- Time 

# Important:
Killing with rocks provides more points
Killing Fygars provide more points if killed horrizontally
"""
    
from tree_search import *    
from consts import *
import math
import random
from path_to_enemies import *

SIZE_X = 48
SIZE_Y = 24

# Returns key
def get_key(map, digdug, enemy, target_neighbors, dug_dir, rocks, step, num_enemies):
    if can_shoot(digdug, enemy, target_neighbors, map, dug_dir):
        return "A"
    else:
        map_path = PathFinder(map, rocks, math.dist(digdug, enemy.get("pos")), step)
        p = SearchProblem(map_path, digdug, enemy.get("pos"))
        t = SearchTree(p)
        
        path = t.search()
        if path is None or []: # check for empty list to avoid index out of range bug when colides but still calculated path
            return " "

        x_dug = digdug[0]
        y_dug = digdug[1]
        next_x = path[1][0]
        next_y = path[1][1]
        key = decide_move(x_dug, y_dug, next_x, next_y, enemy, target_neighbors, rocks, step, num_enemies)
        return key
 
 # Compares enemy positions and returns closest enemy to dug
def enemy_prio(dug, enemies):
    closest_dist = None
    target_enemy = None

    for e in enemies:
        if closest_dist == None:
            closest_dist = math.dist(dug, e.get("pos"))
            target_enemy = e
        elif closest_dist > math.dist(dug, e.get("pos")):
                closest_dist = math.dist(dug, e.get("pos"))
                target_enemy = e

    # Get all enemies within 5 blocks of target enemy
    target_neighbors = [e for e in enemies if e != target_enemy and (math.dist(e.get("pos"), target_enemy.get("pos")) <= 5)]

    return target_enemy, target_neighbors
 
# Get dug dir based on key   
def update_digdug_dir(key):
    if key == "w":
        return Direction.NORTH
    if key == "d":
        return Direction.EAST
    if key == "s":
        return Direction.SOUTH
    if key == "a":
        return Direction.WEST
    return None
    
# Update map state based on key
def update_map(key, map, digdug):
    if key == "a":
        map[digdug[0] - 1][digdug[1]] = 0
        return
    if key == "d":
        map[digdug[0] + 1][digdug[1]] = 0
        return
    if key == "w":
        map[digdug[0]][digdug[1] - 1] = 0
        return
    if key == "s":
        map[digdug[0]][digdug[1] + 1] = 0
        return

def decide_move(x_dug, y_dug, next_x, next_y, enemy, target_neighbors, rocks, step, num_enemies):
    key = " "
    options = []
    if next_x - x_dug == 0 and next_y - y_dug == -1:
        death, options = move_kills_us(next_x, next_y, enemy, target_neighbors, "w", rocks)
        if death:
            key = options[random.randint(0, len(options) - 1)]
            return key
        else:        
            return "w"
    elif next_x - x_dug == 0 and next_y - y_dug == 1:
        death, options = move_kills_us(next_x, next_y, enemy, target_neighbors, "s", rocks)
        if death:
            key = options[random.randint(0, len(options) - 1)]
            return key
        else:        
            return "s"
    elif next_x - x_dug == 1 and next_y - y_dug == 0:
        if enemy.get("name") == "Fygar" and (step >= 1000 or (num_enemies == 1 and step >= 700)): # stuck with smart fygar or fygar trapped with rock
            return "d"
        death, options = move_kills_us(next_x, next_y, enemy, target_neighbors, "d", rocks)
        if death:
            key = options[random.randint(0, len(options) - 1)]
            return key
        else:        
            return "d"
    elif next_x - x_dug == -1 and next_y - y_dug == 0:
        if enemy.get("name") == "Fygar" and (step >= 1000 or (num_enemies == 1 and step >= 700)): # stuck with smart fygar or fygar trapped with rock
            return "a"
        death, options = move_kills_us(next_x, next_y, enemy, target_neighbors, "a", rocks)
        if death:
            key = options[random.randint(0, len(options) - 1)]
            return key
        else:        
            return "a"
        
    return key


# Checks if our next move would kill us
def move_kills_us(next_x, next_y, target_enemy, target_neighbors, key, rocks):
    dangerous_enemies = []
    fygars_list = []
    target_neighbors.append(target_enemy)
    for each in target_neighbors:
        if math.dist([next_x, next_y], each.get("pos")) <= 5: # if distance from digdug to enemy is <= 5, its a dangerous enemy (danger zone)
            dangerous_enemies.append(each)
            if each.get("name") == "Fygar":
                fygars_list.append(each)  # save fygars to check if we are in their fire range
    return check_around(dangerous_enemies, next_x, next_y, key, rocks, fygars_list)

def check_around(dangerous_enemies, next_x, next_y, key, rocks, fygars_list):
    death = False
    options = []
    fire_pos_list = []

    for f in fygars_list:
        en_x = f.get("pos")[0]
        en_y = f.get("pos")[1]
        fire_pos_list = [[x, en_y] for x in range(en_x - 4, en_x + 4) if x>= 0 and x<=47] # 4 because fygar can move and shoot immediately
        
    if [next_x, next_y] in fire_pos_list:
        death = True
    
    for enemy in dangerous_enemies:
        en_x = enemy.get("pos")[0]
        en_y = enemy.get("pos")[1]
        en_dir = enemy.get("dir")
        en_next_x , en_next_y = enemy_next_pos(en_x, en_y, en_dir)
        
        ############## KEY = 'd' #################  
        if key == "d":
            # check behind
            if ((next_x - 2 == en_x and next_y == en_y) or          # behind 1 house, same y
                (next_x - 2 == en_next_x and next_y == en_y) or     # behind 2 houses, same y
                (next_x - 2 == en_x and next_y - 1 == en_y)  or     # behind 1 house, 1 above
                (next_x - 2 == en_x and next_y + 1 == en_y)  or     # behind 1 house, 1 below
                [next_x - 2, next_y] in fire_pos_list):     
                death = True
            else:
                if not (rock_or_out_of_bounds(rocks, next_x - 2, next_y)):
                    options.append("a")
                    
            # check above
            if ((next_x - 1 == en_x and next_y - 1 == en_y) or         # above 1 house, same x
                (next_x - 1 == en_next_x and next_y - 1 == en_y) or    # above 2 houses, same x
                (next_x - 2 == en_x and next_y - 1 == en_y) or         # above 1 house, 1 house behind
                (next_x == en_x and next_y - 1 == en_y) or              # above 1 house, 1 house in front
                [next_x - 1, next_y - 1] in fire_pos_list):             
                death = True
            else:
                if not (rock_or_out_of_bounds(rocks, next_x - 1, next_y - 1)):
                    options.append("w")        
                    
            # check below
            if ((next_x - 1 == en_x and next_y + 1 == en_y) or          # below 1 house, same x
                (next_x - 1 == en_next_x and next_y + 1 == en_y) or     # below 2 houses, same x
                (next_x - 2 == en_x and next_y + 1 == en_y) or          # below 1 house, 1 house behind
                (next_x == en_x and next_y + 1 == en_y) or              # below 1 house, 1 house in front
                [next_x - 1, next_y + 1] in fire_pos_list):               
                death = True
            else:
                if not (rock_or_out_of_bounds(rocks, next_x - 1, next_y + 1)):
                    options.append("s")
                    
            # Check for direct death
            if ((next_x == en_x and next_y == en_y) or
                (next_x == en_next_x and next_y == en_y) or
                (next_x + 1 == en_x and next_y == en_y) or 
                ([next_x, next_y] in fire_pos_list) or
                (rock_or_out_of_bounds(rocks, next_x, next_y))):
                death = True
        
        ############## KEY = 'a' #################  
        elif key == "a":
            # check above
            if ((next_x + 1 == en_x and next_y - 1 == en_y) or         # above 1 house, same x
                (next_x + 1 == en_next_x and next_y - 2 == en_y) or    # above 2 houses, same x
                (next_x + 2 == en_x and next_y - 1 == en_y) or         # above 1 house, 1 house behind
                (next_x == en_x and next_y - 1 == en_y) or              # above 1 house, 1 house in front
                [next_x + 1, next_y - 1] in fire_pos_list):             
                death = True
            else:
                if not (rock_or_out_of_bounds(rocks, next_x + 1, next_y - 1)):
                    options.append("w")  
                    
            # check below
            if ((next_x + 1 == en_x and next_y + 1 == en_y) or          # below 1 house, same x
                (next_x + 1 == en_next_x and next_y + 2 == en_y) or     # below 2 houses, same x
                (next_x + 2 == en_x and next_y + 1 == en_y) or          # below 1 house, 1 house behind
                (next_x == en_x and next_y + 1 == en_y) or              # below 1 house, 1 house in front
                [next_x + 1, next_y + 1] in fire_pos_list):               
                death = True
            else:
                if not (rock_or_out_of_bounds(rocks, next_x + 1, next_y + 1)):
                    options.append("s")
                    
            # check behind
            if ((next_x + 2 == en_x and next_y == en_y) or          # behind 1 house, same y
                (next_x + 2 == en_next_x and next_y == en_y) or     # behind 2 houses, same y
                (next_x + 2 == en_x and next_y - 1 == en_y)  or     # behind 1 house, 1 above
                (next_x + 2 == en_x and next_y + 1 == en_y)  or     # behind 1 house, 1 below
                [next_x + 2, next_y] in fire_pos_list):     
                death = True
            else:
                if not (rock_or_out_of_bounds(rocks, next_x + 2, next_y)):
                    options.append("d")
                    
            # Check for direct death
            if ((next_x == en_x and next_y == en_y) or 
                (next_x == en_next_x and next_y == en_y) or 
                (next_x - 1 == en_x and next_y == en_y) or
                ([next_x, next_y] in fire_pos_list) or
                (rock_or_out_of_bounds(rocks, next_x, next_y))):
                death = True
            
        ############## KEY = 'w' ################# 
        elif key == "w":
            # check behind
            if ((next_x == en_x and next_y + 2 == en_y) or          # below 1 house, same x
                (next_x == en_x and next_y + 2 == en_next_y) or     # below 2 houses, same x
                (next_x - 1 == en_x and next_y + 2 == en_y) or      # below 1 house, 1 house behind
                (next_x + 1 == en_x and next_y + 2 == en_y) or      # below 1 house, 1 house in front
                [next_x, next_y + 2] in fire_pos_list):       
                death = True
            else:
                if not (rock_or_out_of_bounds(rocks, next_x, next_y + 2)):
                    options.append("s")
                    
            # check right
            if ((next_x + 1 == en_x and next_y + 1 == en_y) or          # right 1 house, same x
                (next_x + 1 == en_next_x and next_y + 1 == en_y) or     # right 2 houses, same x
                (next_x + 1 == en_x and next_y == en_y)  or             # right 1 house, 1 above
                (next_x + 1 == en_x and next_y + 2 == en_y) or          # right 1 house, 1 below
                [next_x + 1, next_y + 1] in fire_pos_list):         
                death = True
            else:
                if not (rock_or_out_of_bounds(rocks, next_x + 1, next_y + 1)):
                    options.append("d")
                    
            # check left
            if ((next_x - 1 == en_x and next_y + 1 == en_y) or          # left 1 house, same x
                (next_x - 1 == en_next_x and next_y + 1 == en_y) or     # left 2 houses, same x
                (next_x - 1 == en_x and next_y == en_y)  or             # left 1 house, 1 above
                (next_x - 1 == en_x and next_y + 2 == en_y) or          # left 1 house, 1 below
                [next_x - 1, next_y + 1] in fire_pos_list):         
                death = True
            else:
                if not (rock_or_out_of_bounds(rocks, next_x - 1, next_y + 1)):
                    options.append("a")
            
            # Check for direct death
            if ((next_x == en_x and next_y == en_y) or 
                (next_x == en_x and next_y == en_next_y) or
                (next_x == en_x and next_y - 1 == en_y) or
                ([next_x, next_y] in fire_pos_list) or
                (rock_or_out_of_bounds(rocks, next_x, next_y))):
                death = True
            
        ############## KEY = 's' ################# 
        elif key == "s":
            # check behind
            if ((next_x == en_x and next_y - 2 == en_y) or          # above 1 house, same x
                (next_x == en_x and next_y - 2 == en_next_y) or     # above 2 houses, same x
                (next_x - 1 == en_x and next_y - 2 == en_y) or      # above 1 house, 1 house behind
                (next_x + 1 == en_x and next_y - 2 == en_y) or      # above 1 house, 1 house in front
                [next_x, next_y - 2] in fire_pos_list):       
                death = True
            else:
                if not (rock_or_out_of_bounds(rocks, next_x, next_y - 2)):
                    options.append("w")
        
            # check left
            if ((next_x - 1 == en_x and next_y - 1 == en_y) or          # left 1 house, same x
                (next_x - 1 == en_next_x and next_y - 1 == en_y) or     # left 2 houses, same x
                (next_x - 1 == en_x and next_y - 2 == en_y)  or             # left 1 house, 1 above
                (next_x - 1 == en_x and next_y == en_y) or              # left 1 house, 1 below
                [next_x - 1, next_y - 1] in fire_pos_list):         
                death = True
            else:
                if not (rock_or_out_of_bounds(rocks, next_x - 1, next_y - 1)):
                    options.append("a")
                    
            # check right
            if ((next_x + 1 == en_x and next_y - 1 == en_y) or          # right 1 house, same x
                (next_x + 1 == en_next_x and next_y - 1 == en_y) or     # right 2 houses, same x
                (next_x + 1 == en_x and next_y - 2 == en_y)  or             # right 1 house, 1 above
                (next_x + 1 == en_x and next_y == en_y) or              # right 1 house, 1 below
                [next_x + 1, next_y - 1] in fire_pos_list):         
                death = True
            else:
                if not (rock_or_out_of_bounds(rocks, next_x + 1, next_y - 1)):
                    options.append("d")
                    
            # Check for direct death
            if ((next_x == en_x and next_y == en_y) or
                (next_x == en_x and next_y == en_next_y) or
                (next_x == en_x and next_y + 1 == en_y) or
                ([next_x, next_y] in fire_pos_list) or
                (rock_or_out_of_bounds(rocks, next_x, next_y))):
                death = True
    
    # find which options are valid
    opt_count = {i:options.count(i) for i in options}
    options = []
    
    for opt in opt_count:
        if opt_count.get(opt) == len(dangerous_enemies): # option is valid for all enemies
            options.append(opt)
    
    if len(options) == 0:
        options.append(" ")

    return (death, options)

def rock_or_out_of_bounds(rocks, x, y):
    if x >= SIZE_X or x < 0:
        return True
    elif y >= SIZE_Y or y < 0:
        return True
    for rock in rocks:
        if rock.get("pos") == [x,y]:
            return True
    return False

def enemy_next_pos(en_x, en_y, en_dir):
    next_x = en_x
    next_y = en_y
    if en_dir == Direction.NORTH:
        next_y = en_y - 1
    elif en_dir == Direction.EAST:
        next_x = en_x + 1
    elif en_dir == Direction.SOUTH:
        next_y = en_y + 1
    elif en_dir == Direction.WEST:
        next_x = en_x - 1

    return (next_x, next_y)

def can_shoot(digdug, enemy, target_neighbors, map, dug_dir):
    en_pos = enemy.get("pos")

    if shooting_kills_us(digdug[0], digdug[1], target_neighbors):
        return False
    # Check if map position is block or tunnel (all 4 possibilities)
    if (digdug[1] + 1 < 24) and ((map[digdug[0]][digdug[1] + 1] == 1 and digdug[1] != en_pos[1])):
        return False
    if (digdug[0] + 1 < 48) and (map[digdug[0] + 1][digdug[1]] == 1 and digdug[0] != en_pos[0]):
        return False
    if (map[digdug[0] - 1][digdug[1]] == 1 and digdug[0] != en_pos[0]):
        return False
    if (map[digdug[0]][digdug[1] - 1] == 1 and digdug[1] != en_pos[1]):
        return False

    # Check if we can shoot enemy within 3 spaces
    for i in range(3, 0, -1):
        if ((digdug[0] + i == en_pos[0]) and (digdug[1] == en_pos[1]) and dug_dir == Direction.EAST):
            return True
        if ((digdug[0] == en_pos[0]) and (digdug[1] + i == en_pos[1]) and dug_dir == Direction.SOUTH):
            return True
        if ((digdug[0] - i == en_pos[0]) and (digdug[1] == en_pos[1]) and dug_dir == Direction.WEST):
            return True
        if ((digdug[0] == en_pos[0]) and (digdug[1] - i == en_pos[1]) and dug_dir == Direction.NORTH):
            return True
    return False

def shooting_kills_us(dug_x, dug_y, target_neighbors):
    fire_pos_list = []

    fygars = [e for e in target_neighbors if e.get("name") == "Fygar"]

    for f in fygars:
        en_x = f.get("pos")[0]
        en_y = f.get("pos")[1]
        fire_pos_list = [[x, en_y] for x in range(en_x - 4, en_x + 4) if x>= 0 and x<=47]
        
    if [dug_x, dug_y] in fire_pos_list:
        return True
    
    for enemy in target_neighbors:
        en_x = enemy.get("pos")[0]
        en_y = enemy.get("pos")[1]
            
        if en_x == dug_x and en_y == dug_y - 1:
            return True
        elif en_x == dug_x and en_y == dug_y + 1:
            return True
        elif en_x == dug_x + 1 and en_y == dug_y:
            return True
        elif en_x == dug_x - 1 and en_y == dug_y:
            return True
        
    return False