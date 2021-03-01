import gamelib
import random
import math
import warnings
from sys import maxsize
import json

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
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []

        self.leftOrRight = "R"

        self.isFinished = False

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        # game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        # self.starter_strategy(game_state)
        self.xae12_strategy(game_state)
        game_state.submit_turn()

    def xae12_strategy(self, game_state):
        turret1_locs = [[6, 12], [21, 12]]

        support1_locs = [[14, 4], [13, 3], [14, 3]]

        turret2_locs = [[4, 12], [6, 12], [8, 12], [21, 12], [6, 10]]

        support2_locs = [[14, 4], [15, 4], [13, 3], [14, 3]]

        wall_locs = [[8, 13], [26, 12], [25, 11], [5, 10], [8, 10], [24, 10], [6, 9], [23, 9], [7, 8],
                     [22, 8], [8, 7], [21, 7], [9, 6], [20, 6], [10, 5], [19, 5], [11, 4], [16, 4],
                     [17, 4], [18, 4], [12, 3], [15, 3], [14, 2]]

        wall_locs2 = [[0, 13], [1, 13], [2, 13], [26, 13], [27, 13]]

        # if game_state.get_resource(SP, 0) < 23 and game_state.turn_number != 0:
        if game_state.turn_number <= 5:
            for each in turret1_locs:
                game_state.attempt_spawn(TURRET, each)
            for each in support1_locs:
                game_state.attempt_spawn(SUPPORT, each)

            game_state.attempt_upgrade(support1_locs)

            self.stall_with_interceptors(game_state)

        else:
            for each in turret2_locs:
                game_state.attempt_spawn(TURRET, each)
            for each in support2_locs:
                game_state.attempt_spawn(SUPPORT, each)
            for each in wall_locs:
                game_state.attempt_spawn(WALL, each)

            for each in turret1_locs:
                game_state.attempt_spawn(TURRET, each)
                game_state.attempt_upgrade(each)
            for each in support1_locs:
                game_state.attempt_spawn(SUPPORT, each)
                game_state.attempt_upgrade(each)

            for each in wall_locs2:
                game_state.attempt_spawn(WALL, each)
            for each in wall_locs2:
                game_state.attempt_upgrade(each)
            for each in turret2_locs:
                game_state.attempt_upgrade(each)
            for each in support1_locs:
                game_state.attempt_upgrade(each)
            for each in support2_locs:
                game_state.attempt_upgrade(each)
            for each in turret1_locs:
                game_state.attempt_upgrade(each)

            self.waiting_game(game_state)

    # def xae12_strategy(self, game_state):
    #     turret1_locs = [[6, 12], [21, 12]]
    #
    #     support1_locs = [[14, 4], [13, 3], [14, 3]]
    #
    #     turret2_locs = [[4, 12], [6, 12], [8, 12], [21, 12], [6, 10]]
    #
    #     support2_locs = [[14, 4], [15, 4], [13, 3], [14, 3]]
    #
    #     wall_locs = [[8, 13], [26, 12], [25, 11], [5, 10], [8, 10], [24, 10], [6, 9], [23, 9], [7, 8],
    #                  [22, 8], [8, 7], [21, 7], [9, 6], [20, 6], [10, 5], [19, 5], [11, 4], [16, 4],
    #                  [17, 4], [18, 4], [12, 3], [15, 3], [14, 2]]
    #
    #     if game_state.get_resource(SP, 0) < 23:
    #         for each in turret1_locs:
    #             game_state.attempt_spawn(each)
    #         for each in support1_locs:
    #             game_state.attempt_spawn(each)
    #
    #         game_state.attempt_upgrade(support1_locs)
    #
    #         self.stall_with_interceptors(game_state)
    #
    #     else:
    #         for each in turret1_locs:
    #             game_state.attempt_spawn(each)
    #         for each in support1_locs:
    #             game_state.attempt_spawn(each)
    #
    #         game_state.attempt_upgrade(support1_locs)
    #
    #         self.stall_with_interceptors(game_state)
    #
    #         for each in turret2_locs:
    #             game_state.attempt_spawn(each)
    #         for each in support2_locs:
    #             game_state.attempt_spawn(each)
    #         for each in wall_locs:
    #             game_state.attempt_spawn(each)
    #
    #         self.waiting_game(game_state)

    def waiting_game(self, game_state):
        # Attack moves
        self.remove_front_defences(game_state)
        if game_state.enemy_health >= 30:
            self.midgame_interceptor(game_state)
        else:
            self.find_deficit(game_state)

    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some interceptors early on.
        We will place turrets near locations the opponent managed to score on.
        For offense we will use long range demolishers if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
        """
        if game_state.turn_number <= 15 and (
                self.doesNotSelfDestruct(game_state, [13, 0]) or self.doesNotSelfDestruct(game_state, [14, 0])):
            self.remove_front_defences(game_state)

            ### USE EITHER
            # self.soft_scoutStrat(game_state)
            self.stall_with_interceptors(game_state)

            self.build_defences(game_state)
        else:
            self.remove_front_defences(game_state)
            if game_state.turn_number % 5 == 0:
                self.find_deficit(game_state)

            elif game_state.turn_number % 5 == 1:
                if self.leftOrRight == "L":
                    self.hard_scoutStrat_left(game_state)
                else:
                    self.hard_scoutStrat_right(game_state)
            else:
                self.build_defences(game_state)
                self.build_reactive_defense(game_state)

    def remove_front_defences(self, game_state):
        locs = []
        for y in range(14, 17):
            for x in range(0, 28):
                if game_state.contains_stationary_unit([x, y]):
                    locs.append([x, y])
        gamelib.debug_write(f"locs is {locs}")

        loc_possible = {}
        for y in range(11, 14):
            for x in range(0, 28):
                if len(game_state.get_attackers([x, y], 0)) <= 1:
                    for each in locs:
                        if gamelib.GameMap(game_state.config).distance_between_locations([x, y], each) <= 4.5:
                            if (x, y) not in loc_possible and gamelib.GameMap(game_state.config).in_arena_bounds(
                                    [x, y]):
                                loc_possible[(x, y)] = 1
                            else:
                                if gamelib.GameMap(game_state.config).in_arena_bounds([x, y]):
                                    loc_possible[(x, y)] += 1
        gamelib.debug_write(f"loc_p is {loc_possible}")

        if loc_possible:
            point = max(loc_possible, key=loc_possible.get)
            temp = [point[0], point[1]]

            game_state.attempt_spawn(DEMOLISHER, temp)
            game_state.attempt_spawn(INTERCEPTOR, temp)

    def midgame_interceptor(self, game_state):
        defence_sq = [6, 7]
        launch_sq = [10, 3]
        if game_state.get_resource(MP, 0) >= 5:
            game_state.attempt_spawn(INTERCEPTOR, defence_sq, 2)
            game_state.attempt_spawn(DEMOLISHER, launch_sq, 100000)

    def find_deficit(self, game_state):
        enemy_right_weak = self.find_enemy_defects(game_state, [14, 28], "R")
        enemy_left_weak = self.find_enemy_defects(game_state, [14, 28], "L")

        overall_weaknesses = enemy_left_weak + enemy_right_weak
        total_weaknesses = [0 for _ in range(len(overall_weaknesses))]

        # for i in range(len(total_weaknesses)):
        #     temp = [gamelib.GameMap(game_state.config).distance_between_locations(overall_weaknesses[i], [13, 27]),
        #             gamelib.GameMap(game_state.config).distance_between_locations(overall_weaknesses[i], [14, 27])]
        #     index_min = min(range(len(temp)), key=temp.__getitem__)
        #     total_weaknesses[i] = gamelib.GameMap(game_state.config).TOP_LEFT if index_min == 0 else gamelib.GameMap(
        #         game_state.config).TOP_RIGHT

        starters = [[13, 0], [14, 0]]

        min_opposition_start_left = 0
        min_opposition_start_right = 0

        for each in overall_weaknesses:
            # p = game_state.find_path_to_edge(starters[0], each)
            p = gamelib.ShortestPathFinder().navigate_multiple_endpoints(starters[0], [each], game_state)
            # If it does not self destruct
            if p[-1][1] >= 14:
                # Find the path of least resistance (least attackers)
                min_opposition_start_left += sum(len(game_state.get_attackers(i, 0)) for i in p)

        for each in overall_weaknesses:
            # p = game_state.find_path_to_edge(starters[1], each)
            p = gamelib.ShortestPathFinder().navigate_multiple_endpoints(starters[1], [each], game_state)
            # If it does not self destruct
            if p[-1][1] >= 14:
                # Find the path of least resistance
                s = 0
                min_opposition_start_right = sum(len(game_state.get_attackers(i, 0)) for i in p)

        # Launch an attack from LEFT
        if min_opposition_start_left < min_opposition_start_right:
            self.hard_scoutStrat_clearLeft(game_state)
        # Launch an attack from RIGHT
        else:
            self.hard_scoutStrat_clearRight(game_state)

    def find_enemy_defects(self, game_state, y_range, side):
        holes = []

        if side == "R":
            for i in range(y_range[0], y_range[1]):
                loc = [41 - i, i]
                if not game_state.contains_stationary_unit(loc):
                    holes.append(loc)

        if side == "L":
            for i in range(y_range[0], y_range[1]):
                loc = [-13 + i, i]
                if not game_state.contains_stationary_unit(loc):
                    holes.append(loc)

        return holes

    def hard_scoutStrat_clearLeft(self, game_state):
        self.leftOrRight = "L"
        # if game_state.get_resource(MP, 0) >= 10:
        if game_state.project_future_MP() >= game_state.enemy_health - 5:
            # clear_path = [[27,13],[26,13],[26,12],[25,12],[24,12],[24,11],[25,11]]
            # clear_path = [[12, 1],
            #               [12, 2], [11, 2],
            #               [11, 3], [10, 3],
            #               [10, 4], [9, 4],
            #               [9, 5], [8, 5],
            #               [8, 6], [7, 6],
            #               [7, 7], [6, 7],
            #               [6, 8], [5, 8],
            #               [5, 9], [4, 9],
            #               [4, 10], [3, 10],
            #               [3, 11], [4, 11],
            #               [3, 12], [2, 12], [1, 12],
            #               [2, 13]]
            walls = [[7, 11]]

            turrets = [[6, 11]]
            for loc in walls:
                game_state.attempt_spawn(WALL, loc)
            for loc in turrets:
                game_state.attempt_spawn(TURRET, loc)

            game_state.attempt_upgrade(turrets)
            game_state.attempt_upgrade(walls)

    def hard_scoutStrat_clearRight(self, game_state):
        self.leftOrRight = "R"
        # if game_state.get_resource(MP, 0) >= 10:
        if game_state.project_future_MP() >= game_state.enemy_health - 5:
            # clear_path = [[27,13],[26,13],[26,12],[25,12],[24,12],[24,11],[25,11]]
            # clear_path = [[15, 1],
            #               [15, 2], [16, 2],
            #               [16, 3], [17, 3],
            #               [17, 4], [18, 4],
            #               [18, 5], [19, 5],
            #               [19, 6], [20, 6],
            #               [20, 7], [21, 7],
            #               [21, 8], [22, 8],
            #               [22, 9], [23, 9],
            #               [23, 10], [24, 10],
            #               [23, 11], [24, 11],
            #               [24, 12], [25, 12], [26, 12],
            #               [25, 13]]
            # for loc in clear_path:
            #     game_state.attempt_remove(loc)
            walls = [[1, 12], [3, 12]]

            turrets = [[2, 12]]
            for loc in walls:
                game_state.attempt_spawn(WALL, loc)
            for loc in turrets:
                game_state.attempt_spawn(TURRET, loc)

            game_state.attempt_upgrade(turrets)
            game_state.attempt_upgrade(walls)

    def hard_scoutStrat_left(self, game_state):
        if game_state.get_resource(MP, 0) >= 50:
            mp = game_state.get_resource(MP, 0)
            # game_state.attempt_spawn(DEMOLISHER, [7, 7], math.floor(mp / 2))
            # game_state.attempt_spawn(INTERCEPTOR, [4, 10], 10)
            game_state.attempt_spawn(SCOUT, [14, 0], 1000)
        elif game_state.get_resource(MP, 0) >= game_state.enemy_health:
            # mp = game_state.get_resource(MP, 0)
            # game_state.attempt_spawn(DEMOLISHER, [24,10],int(mp//10))
            # game_state.attempt_spawn(INTERCEPTOR, [22,8],int(mp//10))

            # mp = game_state.get_resource(MP, 0)
            # game_state.attempt_spawn(DEMOLISHER, [7, 7], math.floor(mp / 2))
            # game_state.attempt_spawn(INTERCEPTOR, [4, 10], 1)
            game_state.attempt_spawn(SCOUT, [14, 0], 1000)

    def hard_scoutStrat_right(self, game_state):
        if game_state.get_resource(MP, 0) >= 50:
            mp = game_state.get_resource(MP, 0)
            # game_state.attempt_spawn(DEMOLISHER, [20, 7], math.floor(mp / 2))
            # game_state.attempt_spawn(INTERCEPTOR, [23, 10], 10)
            game_state.attempt_spawn(SCOUT, [13, 0], 1000)
        elif game_state.get_resource(MP, 0) >= game_state.enemy_health:
            # mp = game_state.get_resource(MP, 0)
            # game_state.attempt_spawn(DEMOLISHER, [24,10],int(mp//10))
            # game_state.attempt_spawn(INTERCEPTOR, [22,8],int(mp//10))
            # mp = game_state.get_resource(MP, 0)
            # game_state.attempt_spawn(DEMOLISHER, [20, 7], math.floor(mp / 2))
            # game_state.attempt_spawn(INTERCEPTOR, [23, 10], 1)
            game_state.attempt_spawn(SCOUT, [13, 0], 1000)

    def hard_scoutStrat_part1(self, game_state):
        if game_state.get_resource(MP, 0) >= 20:
            # clear_path = [[27,13],[26,13],[26,12],[25,12],[24,12],[24,11],[25,11]]
            clear_path = [[15, 1], [15, 2], [16, 2], [16, 3], [17, 3], [17, 4], [18, 4], [18, 5], [19, 5], [19, 6],
                          [20, 6], [20, 7], [21, 7], [21, 8], [22, 8], [22, 9], [23, 9], [23, 10], [24, 10], [24, 11],
                          [24, 12], [25, 12], [26, 12], [26, 13], [27, 13]]
            for loc in clear_path:
                game_state.attempt_remove(loc)
        else:
            self.build_defences(game_state)

    def hard_scoutStrat_part2(self, game_state):
        mp = game_state.get_resource(MP, 0)
        if game_state.get_resource(MP, 0) >= 50:
            game_state.attempt_spawn(SCOUT, [13, 0], int(math.floor(mp)))
        if game_state.get_resource(MP,
                                   0) >= 30:  # and self.doesNotSelfDestruct(game_state,[13,0]) and self.doesNotSelfDestruct(game_state,[7,6]):
            # mp = game_state.get_resource(MP, 0)
            # game_state.attempt_spawn(DEMOLISHER, [24,10],int(mp//10))
            # game_state.attempt_spawn(INTERCEPTOR, [22,8],int(mp//10))
            mp = game_state.get_resource(MP, 0)
            game_state.attempt_spawn(SCOUT, [13, 0], int(math.floor(mp / 4)))
            mp = game_state.get_resource(MP, 0)
            for i in range(int(math.floor(mp))):
                game_state.attempt_spawn(SCOUT, [7, 6])
        else:
            self.build_defences(game_state)

    def soft_scoutStrat(self, game_state):
        willNotAttack = True
        if (game_state.get_resource(MP, 0) > 10) and self.doesNotSelfDestruct(game_state, [14, 0]):
            game_state.attempt_spawn(SCOUT, [14, 0], 10)
            willNotAttack = False
        if (game_state.get_resource(MP, 0) > 10) and self.doesNotSelfDestruct(game_state, [13, 0]):
            game_state.attempt_spawn(SCOUT, [13, 0], 10)
            willNotAttack = False
        return willNotAttack

    def doesNotSelfDestruct(self, game_state, loc):
        path = game_state.find_path_to_edge(loc)
        return path[-1][1] >= 14

    def build_defences(self, game_state):

        turret_locations_1 = [[2, 11], [25, 11]]
        wall_locations_1 = [[0, 13], [1, 13], [2, 13], [3, 13], [3, 12], [5, 10], [13, 10], [14, 10], [22, 10],
                            [24, 12], [24, 13], [25, 13], [26, 13], [27, 13]]
        wall_locations_2 = [[0, 13], [1, 13], [2, 13], [3, 13], [24, 13], [25, 13], [26, 13], [27, 13], [1, 12],
                            [2, 12], [3, 12], [4, 12], [23, 12], [24, 12], [25, 12], [26, 12], [3, 11], [4, 11],
                            [5, 11], [22, 11], [23, 11], [24, 11], [5, 10], [7, 10], [8, 10], [9, 10], [11, 10],
                            [12, 10], [13, 10], [14, 10], [15, 10], [16, 10], [17, 10], [18, 10], [19, 10], [20, 10],
                            [22, 10]]
        support_locations_1 = [[13, 2]]
        turret_locations_3 = [[13, 9]]
        turret_locations_2 = [[8, 9], [19, 9]]
        wall_locations_3 = [[6, 9], [7, 9], [9, 9], [10, 9], [11, 9], [12, 9], [14, 9], [15, 9], [16, 9], [17, 9],
                            [18, 9], [20, 9], [21, 9]]
        support_locations_2 = [[13, 3], [14, 2], [14, 3], [15, 4], [16, 5], [17, 6], [18, 7], [19, 8]]
        support_locations_3 = [[12, 4], [11, 5], [10, 5], [10, 6], [9, 7], [8, 8], [7, 7]]

        # game_state.attempt_remove(turret_locations_1)
        for loc in turret_locations_1:
            if game_state.can_spawn(TURRET, loc):
                game_state.attempt_spawn(TURRET, loc)

        # wall_locations = [[0,14],[1,14],[2,14],[3,14],[3,15],[4,16],[5,17],[6,18],[7,17],[8,17],
        # [9,17],[10,17],[11,17],[12,17],[13,17],[14,17],[15,17],[16,17],[17,17],[18,17],[19,17],
        # [20,17],[13,18],[15,18],[21,18],[22,17],[23,16],[24,15],[24,14],[25,14],[26,14],[27,14]]

        # game_state.attempt_remove(turret_locations_1)
        for waller in wall_locations_1:
            if game_state.can_spawn(WALL, waller):
                game_state.attempt_spawn(WALL, waller)

        # game_state.attempt_remove(support_locations_1)
        for loc in support_locations_1:
            if game_state.can_spawn(SUPPORT, loc):
                game_state.attempt_spawn(SUPPORT, loc)

        # game_state.attempt_remove(turret_locations_3)
        for loc in turret_locations_3:
            if game_state.can_spawn(TURRET, loc):
                game_state.attempt_spawn(TURRET, loc)

        game_state.attempt_upgrade(turret_locations_1)
        game_state.attempt_upgrade(turret_locations_3)

        # self.build_reactive_defense(game_state)

        # game_state.attempt_remove(wall_locations_2)
        for waller in wall_locations_2:
            if game_state.can_spawn(WALL, waller):
                game_state.attempt_spawn(WALL, waller)

        # game_state.attempt_remove(turret_locations_2)
        for loc in turret_locations_2:
            if game_state.can_spawn(TURRET, loc):
                game_state.attempt_spawn(TURRET, loc)

        game_state.attempt_upgrade(turret_locations_2)

        # game_state.attempt_remove(wall_locations_3)
        for waller in wall_locations_3:
            if game_state.can_spawn(WALL, waller):
                game_state.attempt_spawn(WALL, waller)

        game_state.attempt_upgrade(wall_locations_1)

        game_state.attempt_spawn(SUPPORT, support_locations_2)
        game_state.attempt_spawn(SUPPORT, support_locations_3)

        game_state.attempt_upgrade(wall_locations_2)
        game_state.attempt_upgrade(wall_locations_3)

        # upgrade walls so they soak more damage
        game_state.attempt_upgrade(support_locations_1)
        game_state.attempt_upgrade(support_locations_2)
        game_state.attempt_upgrade(support_locations_3)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build turret one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1] + 1]
            game_state.attempt_spawn(TURRET, build_location)
            game_state.attempt_upgrade([build_location])

    def stall_with_interceptors(self, game_state):
        """
        Send out interceptors at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(
            game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

        # Remove locations that are blocked by our own structures
        # since we can't deploy units there.
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)

        ct = 0
        # While we have remaining MP to spend lets send out interceptors randomly.
        # while game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP] and len(deploy_locations) > 0:
        #     ct += 1
            # Choose a random deploy location.
        deploy_index = random.randint(0, len(deploy_locations) - 1)
        deploy_location = deploy_locations[deploy_index]

        game_state.attempt_spawn(INTERCEPTOR, deploy_location, 10000)
        """
        We don't have to remove the location since multiple mobile
        units can occupy the same space.
        """

    def demolisher_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our demolisher can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        stationary_units = [WALL, TURRET, SUPPORT]
        cheapest_unit = WALL
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost[game_state.MP] < gamelib.GameUnit(cheapest_unit, game_state.config).cost[game_state.MP]:
                cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our demolisher from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn demolishers next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(DEMOLISHER, [24, 10], 1000)

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
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET,
                                                                                             game_state.config).damage_i
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
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly,
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()