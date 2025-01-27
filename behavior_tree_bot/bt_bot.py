#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn


# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():
    """
    Build a behavior tree that attempts multiple strategies in a single turn:
      1. Defend threatened planets (if needed).
      2. Expand to neutral (if available).
      3. Attack enemy (if available).
    """
    
    # 1) Aggressive Expansion
    expand_seq = Sequence(name='Expand Strategy')
    expand_check = Check(if_neutral_planet_available)
    expand_action = Action(spread_to_best_neutral_planet)
    expand_seq.child_nodes = [expand_check, expand_action]

    # 2) Aggressive Counterattacks
    attack_seq = Sequence(name='Attack Strategy')
    attack_check = Check(if_enemy_planet_available)
    attack_action = Action(attack_newly_acquired_enemy_planets)  # Focus on newly acquired or weak planets
    attack_seq.child_nodes = [attack_check, attack_action]

    # 3) Defense
    defend_seq = Sequence(name='Defend Strategy')
    defend_check = Check(need_defense)
    defend_action = Action(defend_weakest_planet)
    defend_seq.child_nodes = [defend_check, defend_action]

    # Root Strategy: Expand > Attack > Defend
    root = Selector(name='Root Strategy')
    root.child_nodes = [expand_seq, attack_seq, defend_seq]

    logging.info('\n' + root.tree_to_string())
    return root

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
