import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # Attack weakest enemy planets with multiple fleets
    for strongest_planet in sorted(state.my_planets(), key=lambda p: -p.num_ships):  # Sort by strength
        for weakest_planet in sorted(state.enemy_planets(), key=lambda p: p.num_ships):  # Sort by weakness
            if strongest_planet.num_ships > weakest_planet.num_ships + 5:  # Ensure we have enough ships
                issue_order(state, strongest_planet.ID, weakest_planet.ID, weakest_planet.num_ships + 5)
    return True



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
    # Spread to neutral planets with the best growth rate-to-cost ratio
    for strongest_planet in sorted(state.my_planets(), key=lambda p: -p.num_ships):
        for neutral_planet in sorted(state.neutral_planets(), key=lambda p: (p.growth_rate / (p.num_ships + 1)), reverse=True):
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
    # Focus on recently acquired or weak enemy planets
    if not state.my_planets() or not state.enemy_planets():
        return False

    for enemy_planet in sorted(state.enemy_planets(), key=lambda p: p.num_ships):
        for strongest_planet in sorted(state.my_planets(), key=lambda p: -p.num_ships):
            distance = state.distance(strongest_planet.ID, enemy_planet.ID)
            required_ships = enemy_planet.num_ships + distance * enemy_planet.growth_rate + 5

            if strongest_planet.num_ships > required_ships:
                issue_order(state, strongest_planet.ID, enemy_planet.ID, required_ships)
                return True
    return False