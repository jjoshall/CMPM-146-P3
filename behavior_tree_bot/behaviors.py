import sys
import math
sys.path.insert(0, '../')
from planet_wars import issue_order

def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def defend_weakest_planet(state):
    # Find the weakest planet and send reinforcements from the strongest planet
    if not state.my_planets():
        return False

    # Find planet that needs help the most
    threatened_planet = None
    max_deficit = 0
    for my_planet in state.my_planets():
        incoming_enemy = 0
        incoming_friendly = 0
        for efleet in state.enemy_fleets():
            if efleet.destination_planet == my_planet.ID:
                incoming_enemy += efleet.num_ships
        for ffleet in state.my_fleets():
            if ffleet.destination_planet == my_planet.ID:
                incoming_friendly += ffleet.num_ships

        net = my_planet.num_ships + incoming_friendly - incoming_enemy
        if net < max_deficit:
            # planet is behind by -net ships
            threatened_planet = my_planet
            max_deficit = net  # negative or zero
    if not threatened_planet:
        return False

    # If found a threatened planet, pick a planet that can send help
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    if not strongest_planet:
        return False

    # If the "threatened_planet" and "strongest_planet" are the same, no point in transferring
    if strongest_planet.ID == threatened_planet.ID:
        return False

    needed = abs(max_deficit) + 5

    # Check if strongest_planet can afford it
    if strongest_planet.num_ships <= needed:
        return False

    return issue_order(state, strongest_planet.ID, threatened_planet.ID, needed)

def spread_to_best_neutral_planet(state):
    # Aggressively expand to neutral planets while prioritizing proximity and growth rate
    for strongest_planet in sorted(state.my_planets(), key=lambda p: -p.num_ships):
        for neutral_planet in sorted(
            state.neutral_planets(),
            key=lambda p: (p.growth_rate / (p.num_ships + 1)) - state.distance(strongest_planet.ID, p.ID),
            reverse=True,
        ):
            ships_to_send = neutral_planet.num_ships + 5
            if strongest_planet.num_ships > ships_to_send:
                issue_order(state, strongest_planet.ID, neutral_planet.ID, ships_to_send)
                return True
    return False

def attack_strongest_enemy_planet(state):
    # Find the strongest enemy planet and attack it to deny the enemy resources
    if not state.my_planets() or not state.enemy_planets():
        return False

    strongest_enemy = max(state.enemy_planets(),
                          key=lambda p: p.num_ships + p.growth_rate * 10,  # simple weighting
                          default=None)
    if not strongest_enemy:
        return False

    # Send from our single strongest planet:
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    if not strongest_planet or strongest_planet.num_ships < 20:
        # if we don't have enough ships, do nothing
        return False

    # Heuristic: how many ships do we need to succeed
    distance = state.distance(strongest_planet.ID, strongest_enemy.ID)
    required = strongest_enemy.num_ships + distance * strongest_enemy.growth_rate + 5

    if strongest_planet.num_ships > required:
        return issue_order(state, strongest_planet.ID, strongest_enemy.ID, required)
    return False

def attack_newly_acquired_enemy_planets(state):
    # Target weak and newly acquired enemy planets
    if not state.my_planets() or not state.enemy_planets():
        return False

    for enemy_planet in sorted(state.enemy_planets(), key=lambda p: p.num_ships + state.distance(p.ID, 0)):
        for strongest_planet in sorted(state.my_planets(), key=lambda p: -p.num_ships):
            distance = state.distance(strongest_planet.ID, enemy_planet.ID)
            required_ships = enemy_planet.num_ships + distance * enemy_planet.growth_rate + 5

            if strongest_planet.num_ships > required_ships:
                issue_order(state, strongest_planet.ID, enemy_planet.ID, required_ships)
                return True
    return False

def multi_planet_attack(state):
    # Coordinate fleets from multiple planets to overwhelm a target
    if not state.my_planets() or not state.enemy_planets():
        return False

    target = min(state.enemy_planets(), key=lambda p: p.num_ships, default=None)
    if not target:
        return False

    # Coordinate ships from multiple planets
    needed_ships = target.num_ships + 10
    total_ships_sent = 0

    for my_planet in sorted(state.my_planets(), key=lambda p: -p.num_ships):
        if total_ships_sent >= needed_ships:
            break
        available_ships = max(my_planet.num_ships // 2, 0)
        if available_ships > 0:
            issue_order(state, my_planet.ID, target.ID, available_ships)
            total_ships_sent += available_ships

    return total_ships_sent >= needed_ships

def attack_closest_weak_enemy_planet(state):
    # Abort if we have no planets
    if not state.my_planets():
        return False

    # Find the weakest enemy planet
    weak_enemy_planet = min(state.enemy_planets(), key=lambda p: p.num_ships, default=None)
    if not weak_enemy_planet:
        return False

    # Determine the number of ships on the weakest enemy planet
    enemy_planet_ships = weak_enemy_planet.num_ships

    # Find the closest planet with enough ships to attack
    closest_planet = min(
        (planet for planet in state.my_planets() if planet.num_ships > enemy_planet_ships + 3),
        key=lambda p: state.distance(p.ID, weak_enemy_planet.ID),
        default=None
    )

    # Abort if no suitable planet is found
    if not closest_planet:
        return False

    # Issue the order to attack the weakest enemy planet
    return issue_order(state, closest_planet.ID, weak_enemy_planet.ID, enemy_planet_ships + 3)

def expand_and_attack(state):
    # Expand to the weakest neutral planet and attack the weakest enemy planet

    # Sort my planets by the number of ships in ascending order
    owned_planets = sorted(state.my_planets(), key=lambda planet: planet.num_ships)

    # Get all possible planets (neutral or enemy) that are not already being targeted by my fleets
    eligible_attack_planets = sorted(
        [planet for planet in state.not_my_planets()
         if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())],
        key=lambda planet: planet.num_ships
    )

    owned_planet_index = 0
    attack_planet_index = 0

    while owned_planet_index < len(owned_planets) and attack_planet_index < len(eligible_attack_planets):
        my_planet = owned_planets[owned_planet_index]
        attack_target = eligible_attack_planets[attack_planet_index]

        # Calculate the required ships to conquer the target planet
        required_ships = attack_target.num_ships + 1

        # If the target is an enemy planet, consider the distance and growth rate
        if attack_target in state.enemy_planets():
            required_ships += state.distance(my_planet.ID, attack_target.ID) * attack_target.growth_rate

        # If my planet has enough ships, issue the order
        if my_planet.num_ships > required_ships:
            issue_order(state, my_planet.ID, attack_target.ID, required_ships)
            attack_planet_index += 1
        owned_planet_index += 1

    return False
