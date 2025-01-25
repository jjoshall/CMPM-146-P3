import sys
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
    # (1) If we have no planets, do nothing because we lost.
    if not state.my_planets():
        return False
    
    # Identify planet that needs help the most
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
    # for demonstration, choose the single strongest planet
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    if not strongest_planet:
        return False

    # If the "threatened_planet" and "strongest_planet" are the same, no point in transferring
    if strongest_planet.ID == threatened_planet.ID:
        return False

    # We do a rough estimate: how many do we need?
    # If net = -10, we need ~10 ships. Let's add a small buffer.
    needed = abs(max_deficit) + 5

    # Check if strongest_planet can afford it
    if strongest_planet.num_ships <= needed:
        return False

    return issue_order(state, strongest_planet.ID, threatened_planet.ID, needed)