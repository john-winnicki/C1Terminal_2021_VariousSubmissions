import gamelib
import random
import math
import warnings
from sys import maxsize
import json
import queue as Q

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""


class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """
        Read in config and perform any initial setup here
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        self.cores = 0
        self.bits = 0
        self.scored_on_locations = dict()
        self.damaged_on_locations = dict()
        self.sp = False

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        if not len(self.scored_on_locations) == 0:
            for k in self.scored_on_locations:
                gamelib.debug_write(f'My edge at {k} for {self.scored_on_locations[k]} dmg')
            # self.scored_on_locations = dict()
        if not len(self.damaged_on_locations) == 0:
            for k in self.damaged_on_locations:
                dmg = self.damaged_on_locations[k]
                if dmg > 0:
                    gamelib.debug_write(f'My wall at {k} for {dmg} dmg')
            # self.damaged_on_locations = dict()
        game_state = gamelib.GameState(self.config, turn_state)
        # gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        # game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.
        self.cores = game_state.get_resource(0, 0)
        self.bits = game_state.get_resource(1, 0)
        # self.starter_strategy(game_state)
        self.basic_strategy(game_state)
        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def get_cheapest_wall(self, game_state):
        stationary_units = [FILTER, DESTRUCTOR, ENCRYPTOR]
        cheapest_unit = FILTER
        cost = 0
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost < gamelib.GameUnit(cheapest_unit, game_state.config).cost:
                cheapest_unit = unit
                cost = unit_class.cost
        return cheapest_unit, cost

    def basic_strategy(self, game_state):
        if game_state.turn_number >= 1:
            self.replace_defense(game_state)

        if game_state.turn_number == 0:
            self.first_scrambler(game_state)
        else:
            self.normal_attack(game_state)

        self.normal_defence(game_state)
        self.normal_encrypt(game_state)

    def normal_defence(self, game_state):
        destructors_points = [[0, 13], [1, 12]]
        filters_points = [[3, 12], [4, 11], [5, 10], [6, 9], [7, 8], [8, 7], [9, 6], [10, 5], [11, 4], [12, 3], [13, 2]]
        self.build_group_walls(game_state, FILTER, filters_points)
        self.build_group_walls(game_state, FILTER, filters_points, True)
        self.build_group_walls(game_state, DESTRUCTOR, destructors_points)
        self.build_group_walls(game_state, DESTRUCTOR, destructors_points, True)

    def normal_encrypt(self, game_state):
        teal_destructors_points = [[1, 13], [3, 13]]
        self.build_group_walls(game_state, DESTRUCTOR, teal_destructors_points)
        self.build_group_walls(game_state, DESTRUCTOR, teal_destructors_points, True)
        yellow_destructors_points = [[4, 12], [5, 12]]
        self.build_group_walls(game_state, DESTRUCTOR, yellow_destructors_points)
        self.build_group_walls(game_state, DESTRUCTOR, yellow_destructors_points, True)
        yellow_destructors_points = [[4, 13], [6, 11], [7, 10]]
        self.build_group_walls(game_state, DESTRUCTOR, yellow_destructors_points)
        self.build_group_walls(game_state, DESTRUCTOR, yellow_destructors_points, True)
        if game_state.turn_number > 10:
            encryptors_points = [[5, 11], [6, 10], [7, 9], [8, 8], [9, 7], [10, 6], [11, 5], [12, 4], [13, 3]]
            encryptors_points = encryptors_points[::-1]
            self.build_group_walls(game_state, ENCRYPTOR, encryptors_points)
            self.build_group_walls(game_state, ENCRYPTOR, encryptors_points, True)

    def normal_attack(self, game_state):
        enemy_left = self.detect_enemy_unit(game_state, unit_type=DESTRUCTOR, valid_x=[1, 2, 3, 4], valid_y=[14, 15])
        enemy_right = self.detect_enemy_unit(game_state, unit_type=DESTRUCTOR, valid_x=[23, 24, 25, 26],
                                             valid_y=[14, 15])
        is_enempy_left_weak = True if enemy_left < enemy_right else False
        block_my_way = [[2, 12]]
        self.build_group_walls(game_state, FILTER, block_my_way, is_enempy_left_weak)
        game_state.attempt_remove([2, 12])
        game_state.attempt_remove([25, 12])
        r = random.randint(10, 20)
        if self.bits > r:
            if is_enempy_left_weak:
                self.all_in(game_state, PING, [25, 11])
            else:
                self.all_in(game_state, PING, [2, 11])
        elif self.bits > (r / 3 * 2):
            if is_enempy_left_weak:
                game_state.attempt_spawn(EMP, [25, 11], 2)
                game_state.attempt_spawn(SCRAMBLER, [11, 2])
            else:
                game_state.attempt_spawn(EMP, [2, 11], 2)
                game_state.attempt_spawn(SCRAMBLER, [16, 2])

    def first_scrambler(self, game_state):
        locations = [[10, 3], [17, 3]]
        game_state.attempt_spawn(SCRAMBLER, locations)

    def scrambler_stratgy(self, game_state):
        sol = sorted(self.scored_on_locations, key=self.scored_on_locations.get, reverse=True)
        rand = random.randint(1, 2)
        k = 0
        for i in sol:
            if self.scored_on_locations == 0:
                continue
            self.all_in(game_state, SCRAMBLER, [i // 100, i % 100], rand)
            self.scored_on_locations[i] //= 2
            k += 1
            if k > 1:
                break

    def replace_defense(self, game_state):
        # Replace destructor
        for k in self.damaged_on_locations:
            location = [k // 100, k % 100]
            if game_state.contains_stationary_unit(location):
                unit = game_state.contains_stationary_unit(location)
                if unit.health <= gamelib.GameUnit(unit.unit_type, game_state.config).health / 4:
                    game_state.attempt_remove(location)
            else:
                if (location[0] == 25 or location[0] == 2) and location[1] == 12:
                    continue
                self.build_wall(game_state, DESTRUCTOR, location)

    def basic_defense(self, game_state):
        # basic middle
        destructors_points = [[10, 11], [12, 11]]
        filters_points = [[10, 10], [11, 10], [12, 10], [13, 10]]
        self.defense_level(game_state, destructors_points, filters_points)
        # basic left and right
        destructors_points = [[0, 13], [7, 11], [1, 12], [2, 11], [3, 11]]
        filters_points = [[4, 11], [5, 11], [6, 11], [8, 9], [9, 8], [8, 8]]
        self.defense_level(game_state, destructors_points, filters_points)

    def basic_shield(self, game_state, reverse=False):
        locations = []
        for i in range(5, 14):
            locations.append([i, 8])
        self.build_group_walls(game_state, ENCRYPTOR, locations, reverse)
        self.build_group_walls(game_state, ENCRYPTOR, locations, not reverse)

    def t2_attack(self, game_state):
        if self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14]) > 10:
            self.deploy_minions(game_state, EMP, [[2, 11], [25, 11]])
        rand = random.randint(10, 25)
        if self.bits >= rand:
            self.all_in(game_state, PING)

    def t2_defense(self, game_state):
        locations = []
        for i in range(0, 28, 3):
            if i == 13 or i == 14:
                continue
            locations.append([i, 13])
        self.build_group_walls(game_state, DESTRUCTOR, locations)

        reverse = False
        sol = sorted(self.scored_on_locations, key=self.scored_on_locations.get, reverse=True)
        if len(sol) > 0:
            if sol[0] // 100 > 13:
                reverse = True

        locations = []
        for i in range(1, 25, 3):
            locations.append([i, 12])
            locations.append([i + 1, 12])
            if self.cores - len(locations) * 2 <= 14 and game_state.turn_number < 5:
                break
        self.build_group_walls(game_state, DESTRUCTOR, locations, reverse)

        locations = []
        for i in range(5, 20):
            locations.append([i, 8])
            locations.append([i + 2, 6])
        self.build_group_walls(game_state, ENCRYPTOR, locations)

        locations = []
        for i in range(4, 20):
            locations.append([i, 9])
            locations.append([i + 4, 5])
        self.build_group_walls(game_state, ENCRYPTOR, locations)

    def reverse_locations(self, locations):
        rlocations = []
        for location in locations:
            rlocations.append([27 - location[0], location[1]])
        return rlocations

    def encodelocation(self, location):
        return location[0] * 100 + location[1]

    def decodelocation(self, key):
        return [key // 100, key % 100]

    def eculid_distance(self, game_state, key1, key2):
        loc1 = self.decodelocation(key1)
        loc2 = self.decodelocation(key2)
        return game_state.game_map.distance_between_locations(loc1, loc2)

    def advanced_defense(self, game_state):
        destructors = [[3, 13], [1, 12], [2, 12], [2, 11], [3, 11], [4, 9], [5, 9], [6, 9], [7, 9], [8, 9], [9, 9],
                       [10, 9], [11, 9], [12, 9]]
        reversed_destructors = self.reverse_locations(destructors)
        all_locations = destructors + reversed_destructors
        dictionary = dict()
        for location in all_locations:
            dictionary[self.encodelocation(location)] = 999999

        for k in self.scored_on_locations:
            for l in all_locations:
                hashkey = self.encodelocation(l)
                dictionary[hashkey] = min(self.eculid_distance(game_state, hashkey, k), dictionary[hashkey])

        sol = sorted(dictionary, key=dictionary.get)

        spawn_locations = []
        for location in sol:
            spawn_locations.append(self.decodelocation(location))
        self.build_group_walls(game_state, DESTRUCTOR, spawn_locations)

    def defense_level(self, game_state, destructors_points, filters_points):
        basic_wall, cost = self.get_cheapest_wall(game_state)
        self.build_group_walls(game_state, DESTRUCTOR, destructors_points)
        self.build_group_walls(game_state, DESTRUCTOR, destructors_points, True)

        self.build_group_walls(game_state, DESTRUCTOR, filters_points)
        self.build_group_walls(game_state, DESTRUCTOR, filters_points, True)

    def build_group_walls(self, game_state, unit, locations, reverse=False):
        num_success = 0
        wall_locations = []
        for location in locations:
            tmp = location
            if reverse:
                tmp[0] = 27 - tmp[0]
            num_success += self.build_wall(game_state, unit, tmp)
            if num_success > 0:
                wall_locations.append(tmp)

        if num_success > 0:
            gamelib.debug_write(f'Successfully spawn {DESTRUCTOR} {num_success} times')
            gamelib.debug_write(f'Locations are: {wall_locations}')

    def spawn_least_damage(self, game_state):
        num_spawn = self.bits // game_state.type_cost(PING)[1]
        if num_spawn > 10:
            best_location = self.deploy_minions(game_state, PING)
            # if best_location[0] <= 13:
            # self.basic_shield(game_state)
            # else:
            # self.basic_shield(game_state, True)

    def advanced_emp(self, game_state):
        if self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14]) > 10:
            self.deploy_minions(game_state, EMP, [[2, 11], [25, 11]])
        elif self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[15, 16]) > 15:
            self.emp_first_wall(game_state)
            self.deploy_minions(game_state, EMP, [[2, 11], [25, 11]])

    def emp_first_wall(self, game_state, reversed=False):
        locations = []
        for i in range(3, 14, -1):
            locations.append([i, 13])
        self.build_group_walls(game_state, FILTER, locations, reversed)
        self.build_group_walls(game_state, FILTER, locations, not reversed)
        # game_state.attempt_remove(locations)

    def all_in(self, game_state, unit, location=[6, 7], limit=1000):
        num_unit = self.bits // game_state.type_cost(unit)[1]
        num_unit = min(limit, num_unit)
        game_state.attempt_spawn(unit, location, int(num_unit))
        self.bits -= num_unit * game_state.type_cost(unit)[1]

    def special(self, game_state):
        pink_encryptors_points = [[3, 12], [2, 11], [3, 11], [3, 10], [4, 10], [4, 9], [5, 9], [5, 8], [6, 8], [6, 7],
                                  [7, 7], [7, 6], [8, 6], [8, 5], [9, 5], [9, 4], [10, 4], [10, 3], [11, 3], [11, 2],
                                  [12, 2], [12, 1], [13, 1], [13, 0]]
        purple_encryptors_points = [[4, 11], [5, 10], [6, 9], [7, 8], [8, 7], [9, 6], [10, 5], [11, 4], [12, 3],
                                    [13, 2], [14, 1]]
        light_blue_encryptors_points = [[5, 11], [6, 10], [7, 9], [8, 8], [9, 7], [10, 6], [11, 5], [12, 4], [13, 3],
                                        [14, 2], [15, 1]]
        ping_spawn_location_options = [[13, 0], [14, 0]]
        destructor_locations = [[0, 13], [1, 13], [2, 13], [1, 12], [2, 12]]

        best_location = self.least_damage_spawn_location(game_state, ping_spawn_location_options)
        if best_location[0] <= 13:
            pink_encryptors_points = self.reverse_locations(pink_encryptors_points)
            purple_encryptors_points = self.reverse_locations(purple_encryptors_points)
            light_blue_encryptors_points = self.reverse_locations(light_blue_encryptors_points)
            destructor_locations = self.reverse_locations(destructor_locations)

        for location in light_blue_encryptors_points:
            if game_state.contains_stationary_unit(location):
                unit = game_state.contains_stationary_unit(location)
                if not unit.unit_type == ENCRYPTOR:
                    game_state.attempt_remove(location)
        for location in light_blue_encryptors_points:
            if game_state.contains_stationary_unit(location):
                unit = game_state.contains_stationary_unit(location)
                if not unit.unit_type == ENCRYPTOR:
                    game_state.attempt_remove(location)
        for location in pink_encryptors_points:
            if game_state.contains_stationary_unit(location):
                unit = game_state.contains_stationary_unit(location)
                game_state.attempt_remove(location)
        self.build_group_walls(game_state, DESTRUCTOR, destructor_locations)
        self.build_group_walls(game_state, FILTER, purple_encryptors_points)
        self.build_group_walls(game_state, ENCRYPTOR, light_blue_encryptors_points)
        if self.bits > 20:
            if best_location[0] <= 13:
                self.all_in(game_state, SCRAMBLER, [5, 8], 1)
            else:
                self.all_in(game_state, SCRAMBLER, [27 - 5, 8], 1)
            self.all_in(game_state, SCRAMBLER, [5, 8], 1)
            self.all_in(game_state, EMP, best_location, 2)
            self.all_in(game_state, PING, best_location)

    def deploy_minions(self, game_state, unit, friendly_edges=[[13, 0], [14, 0], [12, 1], [15, 1]]):
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        best_location = self.least_damage_spawn_location(game_state, deploy_locations)
        num_spawn = self.bits // game_state.type_cost(unit)[1]
        num_spawn = min(20, num_spawn)
        self.bits -= game_state.type_cost(unit)[1] * game_state.attempt_spawn(unit, best_location, int(num_spawn))
        return best_location

    def build_basic_attackers(self, game_state):
        wall_locations = [0, 12, 15, 27]
        q = Q.PriorityQueue()
        for i in wall_locations:
            q.put((self.distance_x(i, 13.5), i))

        priority_locations = []
        while not q.empty():
            priority_locations.append(q.get()[1])
        # gamelib.debug_write(f'heap queue: {priority_locations}')
        locations = []
        for i in priority_locations:
            y = 10  # good bottom level for destructor
            if i >= 25 or i <= 2:
                y = 13  # toppest level for destructor
            location = [i, y]
            locations.append(location)
        self.build_group_walls(game_state, DESTRUCTOR, locations)

    def build_first_line_cheapest_wall(self, game_state):
        basic_wall, cost = self.get_cheapest_wall(game_state)
        locations = []
        for i in range(0, 27):
            if i >= 12 and i <= 15:
                continue
            location = [i, 11]
            locations.append(location)
        self.build_group_walls(game_state, basic_wall, locations)

    def build_wall(self, game_state, unit, location):
        if not game_state.contains_stationary_unit(location) and game_state.game_map.in_arena_bounds(location):
            if game_state.type_cost(unit)[0] <= self.cores:
                success = game_state.attempt_spawn(unit, location)
                self.cores -= success * game_state.type_cost(unit)[0]
                return success
        return 0

    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some Scramblers early on.
        We will place destructors near locations the opponent managed to score on.
        For offense we will use long range EMPs if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Pings to try and score quickly.
        """
        # First, place basic defenses
        self.build_defences(game_state)
        # Now build reactive defenses based on where the enemy scored
        self.build_reactive_defense(game_state)

        # If the turn is less than 5, stall with Scramblers and wait to see enemy's base
        if game_state.turn_number < 5:
            self.stall_with_scramblers(game_state)
        else:
            # Now let's analyze the enemy base to see where their defenses are concentrated.
            # If they have many units in the front we can build a line for our EMPs to attack them at long range.
            if self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14, 15]) > 10:
                self.emp_line_strategy(game_state)
            else:
                # They don't have many units in the front so lets figure out their least defended area and send Pings there.

                # Only spawn Ping's every other turn
                # Sending more at once is better since attacks can only hit a single ping at a time
                if game_state.turn_number % 2 == 1:
                    # To simplify we will just check sending them from back left and right
                    ping_spawn_location_options = [[13, 0], [14, 0]]
                    best_location = self.least_damage_spawn_location(game_state, ping_spawn_location_options)
                    game_state.attempt_spawn(PING, best_location, 1000)

                # Lastly, if we have spare cores, let's build some Encryptors to boost our Pings' health.
                encryptor_locations = [[13, 2], [14, 2], [13, 3], [14, 3]]
                game_state.attempt_spawn(ENCRYPTOR, encryptor_locations)

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy EMPs can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place destructors that attack enemy units
        destructor_locations = [[0, 13], [27, 13], [8, 11], [19, 11], [13, 11], [14, 11]]
        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        game_state.attempt_spawn(DESTRUCTOR, destructor_locations)

        # Place filters in front of destructors to soak up damage for them
        filter_locations = [[8, 12], [19, 12]]
        game_state.attempt_spawn(FILTER, filter_locations)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build destructor one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1] + 1]
            game_state.attempt_spawn(DESTRUCTOR, build_location)

    def stall_with_scramblers(self, game_state):
        """
        Send out Scramblers at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(
            game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

        # Remove locations that are blocked by our own firewalls
        # since we can't deploy units there.
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)

        # While we have remaining bits to spend lets send out scramblers randomly.
        while game_state.get_resource(game_state.BITS) >= game_state.type_cost(SCRAMBLER)[1] and len(deploy_locations) > 0:
            # Choose a random deploy location.
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]

            game_state.attempt_spawn(SCRAMBLER, deploy_location)
            """
            We don't have to remove the location since multiple information 
            units can occupy the same space.
            """

    def emp_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our EMP's can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        cheapest_unit, cost = self.get_cheapest_wall(game_state)

        # Now let's build out a line of stationary units. This will prevent our EMPs from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn EMPs next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(EMP, [24, 10], 1000)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy destructors that can attack the final location and multiply by destructor damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR,
                                                                                             game_state.config).damage_f #REpl with damage_i
            damages.append(damage)

        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x=None, valid_y=None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (
                            valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at: https://docs.c1games.com/json-docs.html
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        damages = events["damage"]
        self.event_collection(breaches, self.scored_on_locations)
        self.event_collection(damages, self.damaged_on_locations, True)
        '''
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                #gamelib.debug_write("Got scored on at: {}".format(location))
                location = location[0] * 100 + location[1]
                if not location in self.scored_on_locations:
                    self.scored_on_locations[location] = breach[2]
                else:
                    self.scored_on_locations[location] += breach[2]
        '''

    def event_collection(self, events, dictionary, is_wall=False):
        for breach in events:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly,
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if (not unit_owner_self and not is_wall) or (is_wall and unit_owner_self and breach[2] in [0, 1, 2]):
                # gamelib.debug_write("Got scored on at: {}".format(location))
                location = location[0] * 100 + location[1]
                if not location in dictionary:
                    dictionary[location] = breach[2]
                else:
                    dictionary[location] += breach[2]

    def distance_x(self, x1, x2):
        return abs(x1 - x2)

    def emp_new(self, game_state):
        purple_filters_points = [[11, 2], [16, 2], [12, 1], [15, 1], [13, 0], [14, 0]]
        best, points = self.most_cores_spawn_location(game_state, purple_filters_points)
        gamelib.debug_write(f'{best}')
        self.all_in(game_state, EMP, best, 3)

    def most_cores_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            if len(path) < 5:
                continue
            for path_location in path:
                # Get number of enemy destructors that can attack the final location and multiply by destructor damage
                # damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR, game_state.config).damage
                damage -= len(game_state.get_shielders(path_location, 0)) * gamelib.GameUnit(ENCRYPTOR,
                                                                                             game_state.config).health
                # damage -= len(game_state.get_walls(path_location, 0)) * gamelib.GameUnit(FILTER, game_state.config).stability
            damages.append(damage)
        # Now just return the location that takes the least damage
        if len(damages) > 0:
            gamelib.debug_write(
                f'Location for EMP {location_options[damages.index(min(damages))]} will get {min(damages)} points')
        return location_options[damages.index(min(damages))], min(damages)


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()