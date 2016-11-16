import numpy as np
import os
from matplotlib import pyplot as plt


class GeneViewer:
    """
    A class to output the data for genes and to plot them in gene space.
    """
    def __init__(self, world):
        """
        Gene Viewer Initialisation
        :param world: The world being viewed
        """
        self.world = world

        if not os.path.exists(os.path.join('data', self.world.seed)):
            os.makedirs(os.path.join('data', self.world.seed))

    def generate_gene_data(self):
        """Add data for genes for the current world iteration to a list."""

        self.world.bug_gene_data['reproduction_threshold'].append('time=%r' % self.world.time)
        self.world.bug_gene_data['evolutionary_trait'].append(None)
        for bug in self.world.bugList:
            self.world.bug_gene_data['reproduction_threshold'].append(bug.reproduction_threshold)
            self.world.bug_gene_data['evolutionary_trait'].append(None)

    def output_gene_data(self):
        """Output data in CSV (comma-separated values) format for analysis."""

        with open(os.path.join('data', self.world.seed, 'bug_gene_data.csv'), 'a') as bug_gene_file:
            for evolutionary_trait, reproduction_threshold in zip(*self.world.bug_gene_data.values()):
                bug_gene_file.write('%r,' % evolutionary_trait + '%r,' % reproduction_threshold + '\n')

    def plot_gene_data(self):
        """Read the CSV (comma-separated values) output and plot as bar charts in gene space."""

        gene_data = np.genfromtxt(os.path.join('data', self.world.seed, 'bug_gene_data.csv'), delimiter=',',
                                  names=['reproduction_threshold', 'trait'])

        gene_data['reproduction_threshold'][np.isnan(gene_data['reproduction_threshold'])] = -1

#       will turn this into a function later, splits into separate lists based on time
        split_gene_data = []
        for item in gene_data['reproduction_threshold']:
            if item == -1:
                split_gene_data.append([item])
            else:
                split_gene_data[-1].append(item)

#       remove value that allows for splitting lists
        for time_segment in split_gene_data:
            time_segment.remove(-1)

        for i in range(len(split_gene_data)):

#           count number of occurences of each reproduction threshold for each time
            for_plotting = {x: split_gene_data[i].count(x) for x in split_gene_data[i]}
            values, frequencies = for_plotting.keys(), for_plotting.values()
            sum_frequencies = sum(frequencies)
            for_plotting.update((x, y/sum_frequencies) for x, y in for_plotting.items())

#           bar chart
            y_pos = np.arange(len(values))

            plt.bar(y_pos, frequencies, align='center', color='red')
            plt.xticks(y_pos, values)
            plt.xlabel('Reproduction Threshold')
            plt.ylabel('Population')
            plt.title('time=%s' % i)
            plt.savefig(os.path.join('data', self.world.seed, 'gene_data_%s.png' % i))
            plt.close()

            plt.show()
