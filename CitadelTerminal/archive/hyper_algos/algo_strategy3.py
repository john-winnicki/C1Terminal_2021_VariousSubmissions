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
		self.open_channel = 0

		self.path1 = [[0, 13], [1, 13], [1, 12], [2, 12], [2, 11], [3, 11], [3, 10], [4, 10], [4, 9], [5, 9], [5, 8], [6, 8], [6, 7], [7, 7], [7, 6], [8, 6], [8, 5], [9, 5], [9, 4], [10, 4], [10, 3], [11, 3], [11, 2], [12, 2], [12, 1], [13, 1], [14, 1], [13, 0], [14, 0]]
		self.path2 = [[7, 13], [8, 13], [9, 13], [10, 13], [11, 13], [12, 13], [8, 12], [9, 12], [10, 12], [11, 12], [12, 12], [8, 11], [9, 11], [10, 11], [11, 11], [12, 11], [8, 10], [9, 10], [10, 10], [11, 10], [12, 10], [9, 9], [10, 9], [11, 9], [12, 9], [9, 8], [10, 8], [11, 8], [12, 8], [10, 7], [11, 7], [12, 7], [13, 7], [11, 6], [12, 6], [13, 6], [14, 6], [12, 5], [13, 5], [14, 5]]
		self.path3 = [[16, 13], [17, 13], [18, 13], [19, 13], [20, 13], [16, 12], [17, 12], [18, 12], [19, 12], [20, 12], [15, 11], [16, 11], [17, 11], [18, 11], [19, 11], [15, 10], [16, 10], [17, 10], [18, 10], [19, 10], [15, 9], [16, 9], [17, 9], [18, 9], [15, 8], [16, 8], [17, 8], [18, 8], [14, 7], [15, 7], [16, 7], [17, 7], [13, 6], [14, 6], [15, 6], [16, 6], [13, 5], [14, 5], [15, 5]]
		self.path4 = [[26, 13], [27, 13], [25, 12], [26, 12], [24, 11], [25, 11], [23, 10], [24, 10], [22, 9], [23, 9], [21, 8], [22, 8], [20, 7], [21, 7], [19, 6], [20, 6], [18, 5], [19, 5], [17, 4], [18, 4], [16, 3], [17, 3], [15, 2], [16, 2], [13, 1], [14, 1], [15, 1], [13, 0], [14, 0]]
		self.clearings = [self.path1,self.path2,self.path3,self.path4]

		self.interceptors1 = [[4, 9], [6, 7], [8, 5], [10, 3], [12, 1]]
		self.interceptors4 = [[23, 9], [21, 7], [19, 5], [17, 3], [15, 1]]
		self.interceptorShoots = [self.interceptors1,[],[],self.interceptors4]

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

		self.starter_strategy(game_state)

		game_state.submit_turn()


	"""
	NOTE: All the methods after this point are part of the sample starter-algo
	strategy and can safely be replaced for your custom algo.
	"""

	def starter_strategy(self, game_state):
		"""
		For defense we will use a spread out layout and some interceptors early on.
		We will place turrets near locations the opponent managed to score on.
		For offense we will use long range demolishers if they place stationary units near the enemy's front.
		If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
		"""
		if game_state.turn_number<15:
			if self.doesNotSelfDestruct(game_state, [13,0]) or self.doesNotSelfDestruct(game_state, [14,0]):
				self.soft_scoutStrat(game_state)
			self.build_defences(game_state)
		# elif game_state.turn_number%4==0:
		#     self.build_defences(game_state)
		#     self.build_reactive_defense(game_state)
		elif game_state.turn_number==15:
			for loc in self.scored_on_locations:
				game_state.attempt_remove(loc)
			self.scored_on_locations = []
			self.build_defences(game_state)
		else:
			# buildTheDefenses = self.soft_scoutStrat(game_state)
			# buildTheDefenses = True

			if self.open_channel==1 or self.open_channel==2 or self.open_channel==3 or self.open_channel==4:
				self.hard_scoutStrat_part2(game_state)
			elif game_state.get_resource(MP, 0) >= 25 and self.open_channel==0:
				self.hard_scoutStrat_part1(game_state)
			else:
				self.build_defences(game_state)

		# # If the turn is less than 5, stall with interceptors and wait to see enemy's base
		# if game_state.turn_number < 5:
		#     self.stall_with_interceptors(game_state)
		# else:
		#     # Now let's analyze the enemy base to see where their defenses are concentrated.
		#     # If they have many units in the front we can build a line for our demolishers to attack them at long range.
			# if self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14, 15]) > 10:
			#     self.demolisher_line_strategy(game_state)
		#     else:
		#         # They don't have many units in the front so lets figure out their least defended area and send Scouts there.

		#         # Only spawn Scouts every other turn
		#         # Sending more at once is better since attacks can only hit a single scout at a time
		#         if game_state.turn_number % 2 == 1:
		#             # To simplify we will just check sending them from back left and right
		#             scout_spawn_location_options = [[13, 0], [14, 0]]
		#             best_location = self.least_damage_spawn_location(game_state, scout_spawn_location_options)
		#             game_state.attempt_spawn(SCOUT, best_location, 1000)

	# def hard_scoutStrat_part1(self, game_state):
	#     if game_state.get_resource(MP, 0) >= 20:
	#         if self.doesNotSelfDestruct(game_state,[13,0]) and self.doesNotSelfDestruct(game_state,[5,9]):
	#             mp = game_state.get_resource(MP, 0)
	#             game_state.attempt_spawn(DEMOLISHER, [24,10],int(mp//10))
	#             game_state.attempt_spawn(INTERCEPTOR, [22,8],int(mp//10))
	#             mp = game_state.get_resource(MP, 0)
	#             game_state.attempt_spawn(SCOUT,[13,0],int(math.floor(mp/4)))
	#             game_state.attempt_spawn(SCOUT,[5,9],int(3*math.floor(mp/4)))
	#         else:
	#             clear_path = [[27,13],[26,13],[26,12],[25,12],[24,12],[24,11]]
	#             for loc in clear_path:
	#                 game_state.attempt_remove(loc)
	#     else:
	#         self.build_defences(game_state)
	def hard_scoutStrat_part1(self, game_state):

		count1 = self.detect_enemy_unit(game_state, unit_type=None, valid_x=[0,7], valid_y=[14, 21])
		count2 = self.detect_enemy_unit(game_state, unit_type=None, valid_x=[8,13], valid_y=[14, 27])
		count3 = self.detect_enemy_unit(game_state, unit_type=None, valid_x=[14,19], valid_y=[14, 27])
		count4 = self.detect_enemy_unit(game_state, unit_type=None, valid_x=[20,27], valid_y=[14, 21])

		num = 1
		if count1<count2 and count1<count3 and count1<count4:
			num = 1
		elif count2<count3 and count2<count4:
			num = 2
		elif count3<count4:
			num = 3
		else:
			num = 4

		if game_state.get_resource(MP, 0) >= 20:
			for loc in self.clearings[num-1]:
				game_state.attempt_remove(loc)
			if num==2 or num==3:
				game_state.attempt_remove([[13,2],[14,2],[13,3],[14,3],[13,4],[14,4]])
				game_state.attempt_spawn(SUPPORT, [[12,2],[12,3],[15,2],[15,3]])
			self.open_channel = num
		else:
			self.build_defences(game_state)


	def hard_scoutStrat_part2(self, game_state):

		mp = game_state.get_resource(MP, 0)
		if game_state.get_resource(MP, 0) >= 20:
			game_state.attempt_spawn(DEMOLISHER, [14,0], 4)
			game_state.attempt_spawn(SCOUT, [13,0], 1000)
		else:
			self.build_defences(game_state)

		if self.open_channel==2 or self.open_channel==3:
			locs = [[12,2],[12,3],[15,2],[15,3]]
			for loc in locs:
				game_state.attempt_remove(loc)

		if self.open_channel==1 or self.open_channel==4:
			locs = self.interceptorShoots[open_channel-1]
			for loc in locs:
				game_state.attempt_spawn(INTERCEPTOR, loc)

		self.open_channel = 0;


	def soft_scoutStrat(self, game_state):
		willNotAttack = True
		num = random.randint(0,1)
		if (num==0 and game_state.get_resource(MP, 0) >= 5) and self.doesNotSelfDestruct(game_state,[14,0]):
			game_state.attempt_spawn(SCOUT, [14,0], 10)
			willNotAttack = False
		if (num==1 and game_state.get_resource(MP, 0) >= 5) and self.doesNotSelfDestruct(game_state,[13,0]):
			game_state.attempt_spawn(SCOUT, [13,0], 10)
			willNotAttack = False
		return willNotAttack


	def soft_demolisherStrat(self, game_state):
		willNotAttack = True
		if (game_state.get_resource(MP, 0) >= 6) and self.doesNotSelfDestruct(game_state,[14,0]):
			game_state.attempt_spawn(DEMOLISHER, [14,0], 10)
			willNotAttack = False
		if (game_state.get_resource(MP, 0) >= 6) and self.doesNotSelfDestruct(game_state,[13,0]):
			game_state.attempt_spawn(DEMOLISHER, [13,0], 10)
			willNotAttack = False
		return willNotAttack


	def doesNotSelfDestruct(self, game_state, loc):
		path = game_state.find_path_to_edge(loc)
		return path[-1][1]>=14

	def build_defences(self, game_state):

		turret_locations_1 = [[2,11],[25,11]]
		wall_locations_1 = [[0,13],[1,13],[2,13],[3,13],[3,12],[5,10],[13,10],[14,10],[22,10],[24,12],[24,13],[25,13],[26,13],[27,13]]
		wall_locations_2 = [[0,13],[1,13],[2,13],[3,13],[24,13],[25,13],[26,13],[27,13],[1,12],[2,12],[3,12],[4,12],[23,12],[24,12],[25,12],[26,12],[3,11],[4,11],[5,11],[22,11],[23,11],[24,11],[5,10],[7,10],[8,10],[9,10],[11,10],[12,10],[13,10],[14,10],[15,10],[16,10],[17,10],[18,10],[19,10],[20,10],[22,10]]
		support_locations_1 = [[13,2],[14,2],[13,3],[14,3],[13,4],[14,4]]
		turret_locations_3 = [[13,9]]
		turret_locations_2 = [[8,9],[19,9]]
		wall_locations_3 = [[6,9],[7,9],[9,9],[10,9],[11,9],[12,9],[14,9],[15,9],[16,9],[17,9],[18,9],[20,9],[21,9]]
		support_locations_2 = [[13,3],[14,2],[14,3],[15,4],[16,5],[17,6],[18,7],[19,8]]
		support_locations_3 = [[12,4],[11,5],[10,5],[10,6],[9,7],[8,8],[7,7],[20,7]]

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

		# game_state.attempt_remove(turret_locations_3)
		for loc in turret_locations_3:
			if game_state.can_spawn(TURRET, loc):
				game_state.attempt_spawn(TURRET, loc)

		# game_state.attempt_remove(support_locations_1)
		for loc in support_locations_1:
			if game_state.can_spawn(SUPPORT, loc):
				game_state.attempt_spawn(SUPPORT, loc)

		game_state.attempt_upgrade(turret_locations_1)
		game_state.attempt_upgrade(turret_locations_3)

		self.build_reactive_defense(game_state)

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
			build_location = [location[0], location[1]+1]
			game_state.attempt_spawn(TURRET, build_location)

	def stall_with_interceptors(self, game_state):
		"""
		Send out interceptors at random locations to defend our base from enemy moving units.
		"""
		# We can spawn moving units on our edges so a list of all our edge locations
		friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

		# Remove locations that are blocked by our own structures
		# since we can't deploy units there.
		deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)

		# While we have remaining MP to spend lets send out interceptors randomly.
		while game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP] and len(deploy_locations) > 0:
			# Choose a random deploy location.
			deploy_index = random.randint(0, len(deploy_locations) - 1)
			deploy_location = deploy_locations[deploy_index]

			game_state.attempt_spawn(INTERCEPTOR, deploy_location)
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
				damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
			damages.append(damage)

		# Now just return the location that takes the least damage
		return location_options[damages.index(min(damages))]

	def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
		total_units = 0
		for location in game_state.game_map:
			if game_state.contains_stationary_unit(location):
				for unit in game_state.game_map[location]:
					if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
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
