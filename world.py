import datetime
import random
import csv
from utility_methods import *
from direction import Direction
from bug import Bug
from food import Food
from constants import *


class World:
    """
    A class to create in the environment in which our organisms live.
    """

    def __init__(self, rows, columns, seed=None, fertile_lands=None, time=0):
        """
        World Initialisation
        :param rows: Number of rows in the world
        :param columns: Number of columns in the world
        """
        self.columns = columns
        self.rows = rows
        self.time = time
        self.seed = seed if seed is not None else datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.food_taste_average = 180.0
        random.seed(self.seed)

        # Initiate a dict to store lists of food and bugs
        self.organism_lists = {FOOD_NAME: {'alive': [], 'dead': []}, BUG_NAME: {'alive': [], 'dead': []}}
        self.grid = np.zeros(shape=(rows, columns))

        if fertile_lands is None:
            # make the whole world fertile
            self.fertile_squares = [[x, y] for x in range(self.columns) for y in range(self.rows)]
        else:
            self.fertile_squares = []
            for i in fertile_lands:
                min_x, min_y, max_x, max_y = i[0][0], i[0][1], i[1][0], i[1][1]
                self.fertile_squares += [[x, y] for x in range(min_x, max_x + 1) for y in range(min_y, max_y + 1)]

        self.spawnable_squares = list(self.fertile_squares)

    #
    # def fromfile(cls, rows, columns, time, fertile_lands, file_path,
    #              seed=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')):
    #     food_list, bug_list = [], []
    #     with open(file_path, 'r') as f:
    #         reader = csv.reader(f)
    #         for i in reader:
    #             if i[0] == "'food'":
    #                 food_list.append(Food([int(i[1]), int(i[2])], int(i[3]), int(i[4]), 100, float(i[5])))
    #             elif i[0] == "'bug'":
    #                 bug_list.append(Bug([int(i[1]), int(i[2])], int(i[3]), int(i[4]), 100, float(i[5])))
    #
    #     return cls(rows, columns, time, fertile_lands, seed, food_list, bug_list)

    def get_disallowed_directions(self, current_position, organism_type):
        """Each organism cannot collide with itself (no overlap)."""
        disallowed_directions = []

        if self.check_collision(current_position + np.array([0, 1]), organism_type):
            disallowed_directions.append(Direction.up)
        if self.check_collision(current_position + np.array([0, -1]), organism_type):
            disallowed_directions.append(Direction.down)
        if self.check_collision(current_position + np.array([-1, 0]), organism_type):
            disallowed_directions.append(Direction.left)
        if self.check_collision(current_position + np.array([1, 0]), organism_type):
            disallowed_directions.append(Direction.right)

        return disallowed_directions

    def check_collision(self, position, organism_type):
        """Check if position is out of bounds and for disallowed collisions."""
        # collide with wall
        if position[0] < 0 or position[0] >= self.columns or position[1] < 0 or position[1] >= self.rows:
            return True

        # collide with organism of the same type
        if self.grid[tuple(position)] == organism_type or self.grid[tuple(position)] == FOOD_VAL + BUG_VAL:
            return True

        return False

    def available_spaces(self):
        """Get available spawn spaces and the average of the food taste value for ."""
        self.spawnable_squares = list(self.fertile_squares)
        food_taste_list = []

        for food in self.organism_lists[FOOD_NAME]['alive']:

            try:
                self.spawnable_squares.remove(food.position.tolist())
            except ValueError:
                pass
            food_taste_list.append(food.taste)

        if len(food_taste_list) > 0:
            self.food_taste_average = int(get_taste_average(food_taste_list))

    def kill(self, organism):
        self.grid[tuple(organism.position)] -= organism.organism_val
        self.organism_lists[organism.organism_name]['dead'][-1].append(organism)
        self.organism_lists[organism.organism_name]['alive'].remove(organism)

    def spawn(self, organism):
        self.grid[tuple(organism.position)] += organism.organism_val
        self.organism_lists[organism.organism_name]['alive'].append(organism)

    def drop_food(self, number, energy=20, reproduction_threshold=30, energy_max=100, taste=180):
        """Spawn food on fertile land and check spawn square is available."""
        for _ in range(number):
            try:
                spawn_position = self.spawnable_squares.pop(random.randint(0, len(self.spawnable_squares) - 1))
                self.spawn(Food(spawn_position, energy, reproduction_threshold, energy_max, taste))
            except ValueError:
                break

    def drop_bug(self, number, energy=30, reproduction_threshold=70, energy_max=100, taste=180):
        """
        Spawn bugs on fertile land and check spawn square is available, bugs only created upon initialisation.
        random_spawn: set to True to randomly spawn bugs anywhere in the world.
        """

        # TODO: spawn outside fertile lands

        for _ in range(number):
            try:
                spawn_position = self.spawnable_squares.pop(random.randint(0, len(self.spawnable_squares) - 1))
                self.spawn(Bug(spawn_position, energy, reproduction_threshold, energy_max, taste))
            except ValueError:
                break
