import numpy as np


class Organism:
    def __init__(self, position, energy, reproduction_threshold, energy_max):
        self.position = np.array(position)
        self.energy = energy
        self.energy_initial = energy
        self.reproduction_threshold = reproduction_threshold
        self.energy_max = energy_max

    def __repr__(self):
        return '%s-[%s, %s]' % (self.__class__.__name__, self.position[0], self.position[1])

    def reproduce(self, new_pos):
        self.energy = self.energy_initial

        # Set new parameters
        new_energy = self.energy_initial
        new_energy_max = self.energy_max
        new_reproduction_threshold = self.reproduction_threshold

        # Create new object
        return self.__class__(new_pos, new_energy, new_reproduction_threshold, new_energy_max)