

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())


def if_enemy_planet_available(state):
    # Check if there is at least one enemy planet available
    return any(state.enemy_planets())

def need_defense(state):
    # Check if we have at least one planet that is being threatened
    # Check sum of incoming enemy fleets
    # exceeds the ships + incoming friendly fleets.

    for my_planet in state.my_planets():
        incoming_enemy = sum(f.num_ships for f in state.enemy_fleets() if f.destination_planet == my_planet.ID)
        incoming_friendly = sum(f.num_ships for f in state.my_fleets() if f.destination_planet == my_planet.ID)
        if incoming_enemy > (my_planet.num_ships + incoming_friendly):
            return True
    return False

def is_stronger_than_enemy(state):
    # Check if the sum of my ships and incoming friendly fleets
    # is greater than the sum of enemy ships and incoming enemy fleets
    # Kind of like have_largest_fleet, but can be used as a separate check

    my_total = sum(p.num_ships for p in state.my_planets()) + sum(f.num_ships for f in state.my_fleets())
    enemy_total = sum(p.num_ships for p in state.enemy_planets()) + sum(f.num_ships for f in state.enemy_fleets())
    return my_total > enemy_total