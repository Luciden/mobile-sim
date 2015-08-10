__author__ = 'Dennis'

from copy import deepcopy
import csv

from world import World
from log import Log


class SimulationSetting(object):
    def __init__(self):
        self.condition = ""
        self.initial_triggers = []
        self.trigger_additions = {}
        self.trigger_removals = {}

        self.entities = {}
        self.controllers = {}


class SimulationSuite(object):
    """
    Make it easier to run several simulations in succession.

    Attributes
    ----------
    visualizer : Visualizer
        Visualizer that will be used for the simulations.
    simulations : [SimulationSettings]

    Methods
    -------
    run_simulations
        Runs all configured simulations.
    """
    def __init__(self):
        self.visualizer = None

        self.simulation_length = 10

        self.constant_entities = {}
        self.controllers = {}
        self.initial_triggers = {}

        self.conditional_trigger_changes = {}

        self.constant_data_collection = {}
        self.bins = -1

    def set_visualizer(self, visualizer):
        self.visualizer = visualizer

    def set_simulation_length(self, length):
        self.simulation_length = length

    def set_data_bins(self, bins):
        self.bins = bins

    def run_single(self, condition, trigger_condition, controllers):
        self.run_simulations(condition, trigger_condition, controllers)

    def run_multiple(self, condition, trigger_condition, controllers, n):
        for i in range(n):
            self.run_simulations(condition, trigger_condition, controllers, number=i)

    @staticmethod
    def make_average(name, n):
        data_meta = {}
        c = []
        for i in range(n):
            f = open(name + "_{0}_bins".format(str(i)) + ".csv", "rt")
            try:
                # Skip header
                header = f.readline()
                c = [x.rstrip() for x in header.split(' ')[1:]]

                reader = csv.reader(f, delimiter=' ')

                current_data = []
                for row in reader:
                    current_data.append([int(x) for x in row[1:]])

                data_meta[i] = current_data
            finally:
                f.close()

        # Calculate totals and averages
        totals = deepcopy(data_meta[0])
        for i in range(1, n):
            for j in range(len(totals)):
                for k in range(len(c)):
                    totals[j][k] = totals[j][k] + data_meta[i][j][k]

        for i in range(len(totals)):
            for k in range(len(c)):
                totals[i][k] /= float(n)

        Log.write_data(name + "_avg", c, totals)

    def run_simulations(self, only_condition=None, only_trigger_condition=None, only_controllers=None, number=None):
        for setting in self.create_all_settings():
            print "running {0}-{1}".format(setting.condition, setting.trigger_condition)

            # Skip if this is not one of the conditions we want to simulate
            if only_condition is not None and setting.condition != only_condition:
                print "skipping {0}".format(only_condition)
                continue
            if only_controllers is not None:
                is_match = True
                for e in only_controllers:
                    if only_controllers[e] != setting.controllers[e][0]:
                        is_match = False

                if not is_match:
                    print "skipping {0}, {1}".format(only_condition, only_controllers)
                    continue

            world = World(self.visualizer)
            file_name = setting.condition + "-" + setting.trigger_condition

            for entity_name in setting.entities:
                entity = setting.entities[entity_name]()
                if entity_name in setting.controllers:
                    entity.set_agent(setting.controllers[entity_name][1]())
                    file_name += "-{0}-{1}".format(entity_name, setting.controllers[entity_name][0])

                world.add_entity(entity)

            for trigger in setting.initial_triggers:
                world.add_trigger(*trigger)

            if only_trigger_condition is not None and setting.trigger_condition != only_trigger_condition:
                print "skipping {0}".format(only_trigger_condition)
                continue
            world.run(self.simulation_length, add_triggers=setting.trigger_additions, remove_triggers=setting.trigger_removals)

            log = world.log
            log.make_data(file_name, self.constant_data_collection, number)
            Log.make_bins(file_name, self.constant_data_collection.values(), self.bins, number)

    def create_all_settings(self):
        settings = []
        updated_settings = []

        for condition in self.initial_triggers:
            setting = SimulationSetting()
            setting.condition = condition
            setting.initial_triggers = self.initial_triggers[condition]

            setting.entities = {}
            for entity_name in self.constant_entities:
                setting.entities[entity_name] = self.constant_entities[entity_name]

            if condition in self.conditional_trigger_changes:
                original = deepcopy(setting)
                for trigger_condition in self.conditional_trigger_changes[condition]:
                    setting = deepcopy(original)
                    setting.trigger_condition = trigger_condition
                    setting.trigger_additions.update(self.conditional_trigger_changes[condition][trigger_condition][0])
                    setting.trigger_removals.update(self.conditional_trigger_changes[condition][trigger_condition][1])

                    settings.append(setting)
            else:
                settings.append(setting)

        for i in range(len(settings)):
            setting = settings.pop()

            for entity_name in setting.entities:
                for controller in self.controllers[entity_name]:
                    updated = deepcopy(setting)
                    updated.controllers[entity_name] = (controller, self.controllers[entity_name][controller])
                    updated_settings.append(updated)

        settings = updated_settings

        return settings

    def add_constant_entities(self, entities):
        """
        Parameters
        ----------
        entities : {string: function : Entity}
        """
        self.constant_entities.update(entities)
        for entity in self.constant_entities:
            self.controllers[entity] = {}

    def add_controllers(self, entity_name, controllers):
        """
        Parameters
        ----------
        entity_name : string
        controllers : {string; function : Controller}
        """
        self.controllers[entity_name].update(controllers)

    def add_constant_data_collection(self, attribute_names, column_labels):
        """
        Parameters
        ----------
        entity_name : string
        attribute_names : [string]
        column_labels : [string]
            Should be same size as attribute names list.
        """
        self.constant_data_collection.update(dict(zip(attribute_names, column_labels)))

    def add_initial_triggers(self, triggers):
        self.initial_triggers.update(triggers)

    def add_conditional_trigger_changes(self, changes):
        """
        Parameters
        ----------
        condition_name : string
        changes : {int: ([trigger], [trigger])}
            Lists for every condition, for every time what the triggers are that are
            added and removed respectively.
        """
        self.conditional_trigger_changes.update(changes)
