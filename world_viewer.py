import numpy as np
import os
import sys
import csv
import colorsys
import fnmatch
from matplotlib import pyplot as plt
from matplotlib import collections as col
import config as cfg
from constants import FOOD_NAME, BUG_NAME


class WorldViewer:
    """
    A class to read data outputs and plot the results.
    """

    def __init__(self, seed):
        """
        World Viewer Initialisation
        :param seed: The seed value for data to output
        """
        self.seed = seed

        # World plotting axis initialisation
        self.ax = plt.figure(figsize=(cfg.fig_size, cfg.fig_size)).add_subplot(1, 1, 1)
        self.ax.set_xlim(0, cfg.world['settings']['columns'])
        self.ax.set_ylim(0, cfg.world['settings']['rows'])
        # Turn off axis labels
        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)

    def view_world(self, world):
        """"Plot the world: rectangles=food, circles=bugs."""

        # Food parameters for plotting
        if world.organism_lists[FOOD_NAME]['alive']:
            food_x_offsets, food_y_offsets, food_facecolors = ([] for _ in range(3))

            for food in world.organism_lists[FOOD_NAME]['alive']:
                hue = float(food.taste) / 360 if cfg.food['evolve_taste'] else 0.33  # else green
                # Luminosity of plant depends on energy
                luminosity = 0.9 - food.energy * 0.004 if food.energy > 20 else 0.82  # maximum luminosity value

                food_x_offsets.append(food.position[0] + 0.5)
                food_y_offsets.append(food.position[1] + 0.5)
                food_facecolors.append(
                    'k') if cfg.check_newly_spawned_plants and food.lifetime == 1 else food_facecolors.append(
                    colorsys.hls_to_rgb(hue, luminosity, 1))

            # Add final parameters, and create and plot collection
            food_sizes = np.full(len(food_x_offsets), (
                (cfg.fig_size * 1e5) / (cfg.world['settings']['columns'] * cfg.world['settings']['rows'])),
                                 dtype=np.int)
            food_linewidths = np.zeros(len(food_x_offsets))
            food_collection = col.RegularPolyCollection(4, rotation=np.pi / 4, sizes=food_sizes,
                                                        offsets=list(zip(food_x_offsets, food_y_offsets)),
                                                        transOffset=self.ax.transData, facecolors=food_facecolors,
                                                        linewidths=food_linewidths)
            self.ax.add_collection(food_collection)

        # Bug parameters for plotting
        if world.organism_lists[BUG_NAME]['alive']:
            bug_widths, bug_heights, bug_x_offsets, bug_y_offsets, bug_facecolors = ([] for _ in range(5))

            for bug in world.organism_lists[BUG_NAME]['alive']:

                # Size of bug depends on energy
                bug_size = bug.energy * 0.01
                if bug_size < 0.3:
                    bug_size = 0.3
                elif bug_size > 1.0:
                    bug_size = 1.0

                bug_widths.append(bug_size)
                bug_heights.append(bug_size)
                bug_x_offsets.append(bug.position[0] + 0.5)
                bug_y_offsets.append(bug.position[1] + 0.5)

                if cfg.bug['evolve_taste']:  # black outline with coloured dot in centre
                    bug_facecolors.append('k')

                    bug_widths.append(bug_size / 1.5)
                    bug_heights.append(bug_size / 1.5)
                    bug_x_offsets.append(bug.position[0] + 0.5)
                    bug_y_offsets.append(bug.position[1] + 0.5)
                    bug_facecolors.append(
                        'k') if cfg.check_newly_spawned_bugs and bug.lifetime == 1 else bug_facecolors.append(
                        colorsys.hls_to_rgb(float(bug.taste) / 360, 0.5, 1))

                else:  # no outline
                    bug_facecolors.append(
                        'k') if cfg.check_newly_spawned_bugs and bug.lifetime == 1 else bug_facecolors.append('r')

            # Add final parameters, and create and plot collection
            bug_angles = np.zeros(len(bug_widths))
            bug_linewidths = np.zeros(len(bug_widths))
            bug_collection = col.EllipseCollection(bug_widths, bug_heights, bug_angles, units='xy',
                                                   offsets=list(zip(bug_x_offsets, bug_y_offsets)),
                                                   transOffset=self.ax.transData, facecolors=bug_facecolors,
                                                   linewidths=bug_linewidths)
            self.ax.add_collection(bug_collection)

        plt.title('time=%s' % world.time, fontsize=30)
        plt.savefig(os.path.join('data', world.seed, 'world', '%s.png' % world.time))
        plt.cla()

    def plot_world_stats(self):
        """Read the CSV (comma-separated values) data files and plot the world statistics."""

        print('reading & plotting world statistics...')

        # Create output directory if it doesn't exist
        if not os.path.exists(os.path.join('data', self.seed, 'world_statistics')):
            os.makedirs(os.path.join('data', self.seed, 'world_statistics'))

        data = [(np.genfromtxt(os.path.join('data', self.seed, 'data_files', path + '.csv'), delimiter=',',
                               names=['time', 'energy', 'population', 'deaths', 'average_deaths',
                                      'average_alive_lifetime', 'average_lifespan', 'average_reproduction_threshold']))
                for path in ['food_data', 'bug_data']]
        food_data, bug_data = data[0], data[1]

        data_to_plot = []
        time = food_data['time']
        world_capacity = cfg.world['settings']['rows'] * cfg.world['settings']['columns']  # normalise for world size

        data1 = [(food_data['population'] / world_capacity, 'Alive')]
        data_to_plot.append({'data': data1, 'x_label': 'Time', 'y_label': 'Population Density', 'y_lim': [0, 1],
                             'title': 'Alive Plant Populations', 'filename': 'food_alive_population.png'})

        data2 = [(bug_data['population'] / world_capacity, 'Alive')]
        data_to_plot.append({'data': data2, 'x_label': 'Time', 'y_label': 'Population Density', 'y_lim': [0, 1],
                             'title': 'Alive Bug Populations', 'filename': 'bug_alive_population.png'})

        data3 = [(food_data['energy'], 'Alive')]
        data_to_plot.append({'data': data3, 'x_label': 'Time', 'y_label': 'Energy', 'y_lim': None,
                             'title': 'Plant Energy', 'filename': 'food_energy.png'})

        data4 = [(bug_data['energy'], 'Alive')]
        data_to_plot.append({'data': data4, 'x_label': 'Time', 'y_label': 'Energy', 'y_lim': None,
                             'title': 'Bug Energy', 'filename': 'bug_energy.png'})

        data5 = [(food_data['deaths'] / world_capacity, 'Deaths')]
        data_to_plot.append({'data': data5, 'x_label': 'Time', 'y_label': 'Population Density', 'y_lim': [0, 1],
                             'title': 'Dead Plant Populations', 'filename': 'food_dead_population.png'})

        data6 = [(bug_data['deaths'] / world_capacity, 'Deaths')]
        data_to_plot.append({'data': data6, 'x_label': 'Time', 'y_label': 'Population Density', 'y_lim': [0, 1],
                             'title': 'Dead Bug Populations', 'filename': 'bug_dead_population.png'})

        # Plot average deaths because otherwise dead plant population is not viewable on the plot (dominated by alive)
        data7 = [(food_data['population'] / world_capacity, 'Alive'),
                 (food_data['average_deaths'] / world_capacity, 'Deaths (last 10 cycles)')]
        data_to_plot.append({'data': data7, 'x_label': 'Time', 'y_label': 'Population Density', 'y_lim': [0, 1],
                             'title': 'Plant Populations', 'filename': 'food_populations.png'})

        data8 = [(bug_data['population'] / world_capacity, 'Alive'),
                 (bug_data['average_deaths'] / world_capacity, 'Deaths (last 10 cycles)')]
        data_to_plot.append({'data': data8, 'x_label': 'Time', 'y_label': 'Population Density', 'y_lim': [0, 1],
                             'title': 'Bug Populations', 'filename': 'bug_populations.png'})

        data9 = [(food_data['average_alive_lifetime'], 'Alive'),
                 (food_data['average_lifespan'], 'Average Lifespan (last 10 cycles)')]
        data_to_plot.append({'data': data9, 'x_label': 'Time', 'y_label': 'Average Lifetime', 'y_lim': None,
                             'title': 'Plant Lifetimes', 'filename': 'food_lifetime.png'})

        data10 = [(bug_data['average_alive_lifetime'], 'Alive'),
                  (bug_data['average_lifespan'], 'Average Lifespan (last 10 cycles)')]
        data_to_plot.append({'data': data10, 'x_label': 'Time', 'y_label': 'Average Lifetime', 'y_lim': None,
                             'title': 'Bug Lifetimes', 'filename': 'bug_lifetime.png'})

        data11 = [(food_data['average_reproduction_threshold'], 'Alive')]
        data_to_plot.append({'data': data11, 'x_label': 'Time', 'y_label': 'Reproduction Threshold', 'y_lim': None,
                             'title': 'Plant Reproduction Threshold', 'filename': 'food_reproduction_threshold.png'})

        data12 = [(bug_data['average_reproduction_threshold'], 'Alive')]
        data_to_plot.append({'data': data12, 'x_label': 'Time', 'y_label': 'Reproduction Threshold', 'y_lim': None,
                             'title': 'Bug Reproduction Threshold', 'filename': 'bug_reproduction_threshold.png'})

        data13 = [(food_data['population'] / world_capacity, 'Plants'),
                  (bug_data['population'] / world_capacity, 'Bugs')]
        data_to_plot.append({'data': data13, 'x_label': 'Time', 'y_label': 'Population Density', 'y_lim': [0, 1],
                             'title': 'World Population', 'filename': 'world_population.png'})

        data14 = [(food_data['energy'] / world_capacity, 'Plants'), (bug_data['energy'] / world_capacity, 'Bugs')]
        data_to_plot.append({'data': data14, 'x_label': 'Time', 'y_label': 'Energy', 'y_lim': None,
                             'title': 'World Energy', 'filename': 'world_energy.png'})

        data15 = [(food_data['average_alive_lifetime'], 'Plants'), (bug_data['average_alive_lifetime'], 'Bugs')]
        data_to_plot.append({'data': data15, 'x_label': 'Time', 'y_label': 'Average Lifetime', 'y_lim': None,
                             'title': 'World Lifetimes', 'filename': 'world_lifetime.png'})

        for data_dict in data_to_plot:
            plt.figure()
            for (y, l) in data_dict['data']:
                plt.plot(time, y, label=l)
            plt.xlabel(data_dict['x_label'])
            plt.ylabel(data_dict['y_label'])
            plt.ylim(data_dict['y_lim'])
            plt.legend(loc=0)
            plt.title(data_dict['title'])
            plt.savefig(os.path.join('data', self.seed, 'world_statistics', data_dict['filename']))
            plt.close()

    def plot_day_data(self, day=None, world=False):
        """
        Reads a CSV (comma-separated values) data file and plot the world and/or gene values for that time.
        :param day: The time to plot
        :param world: Set to True to plot the world
        """

        # Check world parameter and evolution switches
        if world or cfg.food['evolve_reproduction_threshold'] or cfg.food['evolve_taste'] or \
                cfg.bug['evolve_reproduction_threshold'] or cfg.bug['evolve_taste']:

            # Create output directories if they don't exist
            for switch in ['evolve_reproduction_threshold', 'evolve_taste']:
                if cfg.food[switch]:
                    if not os.path.exists(os.path.join('data', self.seed, 'food_' + str(switch.replace("'", "")))):
                        os.makedirs(os.path.join('data', self.seed, 'food_' + str(switch.replace("'", ""))))
                if cfg.bug[switch]:
                    if not os.path.exists(os.path.join('data', self.seed, 'bug_' + str(switch.replace("'", "")))):
                        os.makedirs(os.path.join('data', self.seed, 'bug_' + str(switch.replace("'", ""))))

            # Create the list of organisms for each day
            world_file = csv.reader(open(os.path.join('data', self.seed, 'data_files', 'world_data', '%r.csv' % day)),
                                    delimiter=',')

            organism_list = []
            for row in world_file:
                row.remove(row[-1])  # remove the '\n' for CSV files
                organism_list.append(row)

            organism_list = [[float(organism[i]) if i > 0 else organism[i] for i in range(len(organism))] for organism
                             in organism_list]  # convert text values to floats

        # Plot the world
        if world:

            food_x_offsets, food_y_offsets, food_facecolors = ([] for _ in range(3))
            bug_widths, bug_heights, bug_x_offsets, bug_y_offsets, bug_facecolors = ([] for _ in range(5))

            for organism in organism_list:

                # Food parameters for plotting
                if organism[0] == "'food'":
                    hue = float(organism[5]) / 360 if cfg.food['evolve_taste'] else 0.33  # else green
                    # Luminosity of plant depends on energy
                    luminosity = 0.9 - organism[3] * 0.004 if organism[3] > 20 else 0.82  # maximum luminosity value

                    food_x_offsets.append(organism[1] + 0.5)
                    food_y_offsets.append(organism[2] + 0.5)
                    food_facecolors.append(colorsys.hls_to_rgb(hue, luminosity, 1))

                # Bug parameters for plotting
                elif organism[0] == "'bug'":

                    # Size of bug depends on energy
                    bug_size = organism[3] * 0.01
                    if bug_size < 0.3:
                        bug_size = 0.3
                    elif bug_size > 1.0:
                        bug_size = 1.0

                    bug_widths.append(bug_size)
                    bug_heights.append(bug_size)
                    bug_x_offsets.append(organism[1] + 0.5)
                    bug_y_offsets.append(organism[2] + 0.5)

                    if cfg.bug['evolve_taste']:  # black outline with coloured dot in centre
                        bug_facecolors.append('k')

                        bug_widths.append(bug_size / 1.5)
                        bug_heights.append(bug_size / 1.5)
                        bug_x_offsets.append(organism[1] + 0.5)
                        bug_y_offsets.append(organism[2] + 0.5)
                        bug_facecolors.append(colorsys.hls_to_rgb(float(organism[5]) / 360, 0.5, 1))

                    else:  # no outline
                        bug_facecolors.append('r')

            # Add final parameters
            food_sizes = np.full(len(food_x_offsets), (
                (cfg.fig_size * 1e5) / (cfg.world['settings']['columns'] * cfg.world['settings']['rows'])),
                                 dtype=np.int)
            food_linewidths = np.zeros(len(food_x_offsets))
            bug_angles = np.zeros(len(bug_widths))
            bug_linewidths = np.zeros(len(bug_widths))

            # Create and plot collections
            if food_x_offsets:
                food_collection = col.RegularPolyCollection(4, rotation=np.pi / 4, sizes=food_sizes,
                                                            offsets=list(zip(food_x_offsets, food_y_offsets)),
                                                            transOffset=self.ax.transData,
                                                            facecolors=food_facecolors,
                                                            linewidths=food_linewidths)
                self.ax.add_collection(food_collection)
            if bug_widths:
                bug_collection = col.EllipseCollection(bug_widths, bug_heights, bug_angles, units='xy',
                                                       offsets=list(zip(bug_x_offsets, bug_y_offsets)),
                                                       transOffset=self.ax.transData, facecolors=bug_facecolors,
                                                       linewidths=bug_linewidths)
                self.ax.add_collection(bug_collection)

            plt.title('time=%s' % day, fontsize=30)
            plt.savefig(os.path.join('data', self.seed, 'world', '%s.png' % day))
            plt.cla()

        # Plot genes
        if cfg.food['evolve_reproduction_threshold'] or cfg.food['evolve_taste'] or \
                cfg.bug['evolve_reproduction_threshold'] or cfg.bug['evolve_taste']:

            # Create lists of food and bug gene data for plotting
            food_list, bug_list = [], []

            for organism in organism_list:
                if organism[0] == "'food'":
                    food_list.append(organism)
                elif organism[0] == "'bug'":
                    bug_list.append(organism)

            data_to_plot = [
                {'data': food_list, 'switch': cfg.food, 'path': 'food_evolve_reproduction_threshold', 'colour': 'g',
                 'path2': 'food_evolve_taste', 'colour_maps': 'Greens'},
                {'data': bug_list, 'switch': cfg.bug, 'path': 'bug_evolve_reproduction_threshold', 'colour': 'r',
                 'path2': 'bug_evolve_taste', 'colour_maps': 'Reds'}]

            for organism_data in data_to_plot:  # for food and bugs

                rep_thresh = [organism[4] for organism in organism_data['data']]
                max_rep_thresh = int(max(rep_thresh)) if rep_thresh else 0

                # 1D Plot (bar chart)
                if organism_data['switch']['evolve_reproduction_threshold']:

                    # Reproduction threshold dictionary sets axis plot range
                    rep_dict = {j: 0 for j in range(101)} if max_rep_thresh <= 100 else {j: 0 for j in
                                                                                         range(max_rep_thresh + 1)}

                    for organism in organism_data['data']:
                        # Count number of occurrences of each reproduction threshold
                        rep_dict[organism[4]] += 1

                    y_pos = np.arange(len(rep_dict.keys()))  # set centre values for bars
                    total = sum(rep_dict.values())
                    if total > 0:
                        for key, value in rep_dict.items():
                            rep_dict[key] = value / total  # normalisation

                    plt.figure()
                    plt.bar(y_pos, rep_dict.values(), align='center', color=organism_data['colour'])
                    if not rep_thresh:
                        plt.ylim(0, 1)
                    plt.xlabel('Reproduction Threshold')
                    plt.ylabel('Population')
                    plt.title('time=%s' % day)
                    plt.savefig(os.path.join('data', self.seed, organism_data['path'], '%s.png' % day))
                    plt.close()

                # 2D Plot (heat map)
                if organism_data['switch']['evolve_taste']:

                    # Create lists of gene data
                    taste = [organism[5] for organism in organism_data['data']]

                    # Create and set co-ordinate values in gene space
                    x = [j for j in range(51)] if max_rep_thresh <= 100 else [j for j in
                                                                              range((int(max_rep_thresh / 2) + 1))]
                    y = [j for j in range(61)]

                    # Bin values into binned co-ordinate values
                    rep_thresh = [int(j / 2) for j in rep_thresh]
                    taste = [int(j / 6) for j in taste]

                    # Set 2D co-ordinate values
                    z = [[0 for _ in range(len(x))] for _ in range(len(y))]
                    z_list = [list(j) for j in zip(rep_thresh, taste)]

                    # Update population frequencies
                    for coordinates in z_list:
                        z[coordinates[1]][coordinates[0]] += 1 / len(z_list)

                    # Expand binned data to fit plot
                    x = [j * 2 for j in x]
                    y = [j * 6 for j in y]

                    xi, yi = np.meshgrid(x, y)
                    zi = np.array(z)

                    plt.figure()
                    plt.pcolormesh(xi, yi, zi, cmap=organism_data['colour_maps'])
                    plt.colorbar()
                    plt.xlim(0, 100) if max_rep_thresh <= 100 else plt.xlim(0, max_rep_thresh)
                    plt.ylim(0, 360)
                    plt.xlabel('Reproduction Threshold')
                    plt.ylabel('Taste')
                    plt.title('time=%s' % day)
                    plt.savefig(os.path.join('data', self.seed, organism_data['path2'], '%s.png' % day))
                    plt.close()

    def plot_world_data(self, days=None, start=0, plot_world=False):
        """
        Plot the data for a range of times.
        :param days: Number of days to plot
        :param start: Start time
        :param plot_world: Set to True to plot the world
        """

        # Counts number of CSV (comma-separated values) data files, equivalent to the total number of days simulated
        total_days = len(
            fnmatch.filter(os.listdir(os.path.join('data', self.seed, 'data_files', 'world_data')), '*.csv'))

        if days is None or days > total_days:
            days = total_days - start

        # Plot the data for each day
        for i in range(days):
            sys.stdout.write(
                '\r' + 'reading & plotting world data, time: %r' % (start + i) + '/%r' % (total_days - 1) + '...')
            sys.stdout.flush()
            self.plot_day_data(day=start + i, world=plot_world)
