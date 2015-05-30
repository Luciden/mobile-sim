__author__ = 'Dennis'

from copy import deepcopy

from world import World
from log import Log


class SimulationSetting(object):
    def __init__(self):
        self.condition = ""
        self.initial_triggers = []
        self.trigger_changes = {}

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

    def run_single(self, condition, controllers):
        self.run_simulations(condition, controllers)

    def run_simulations(self, only_condition=None, only_controllers=None):
        for setting in self.create_all_settings():
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
            file_name = setting.condition

            for entity_name in setting.entities:
                entity = setting.entities[entity_name]()
                if entity_name in setting.controllers:
                    entity.set_agent(setting.controllers[entity_name][1]())
                    file_name += "-{0}-{1}".format(entity_name, setting.controllers[entity_name][0])

                world.add_entity(entity)

            for trigger in setting.initial_triggers:
                world.add_trigger(*trigger)

            world.run(self.simulation_length)

            log = world.log
            log.make_data(file_name, self.constant_data_collection)
            Log.make_bins(file_name, self.constant_data_collection.values(), self.bins)

    def create_all_settings(self):
        settings = []
        updated_settings = []

        for condition in self.initial_triggers:
            setting = SimulationSetting()
            setting.condition = condition
            setting.initial_triggers = self.initial_triggers[condition]
            if condition in self.conditional_trigger_changes:
                setting.trigger_changes.update(self.conditional_trigger_changes[condition])

            setting.entities = {}
            for entity_name in self.constant_entities:
                setting.entities[entity_name] = self.constant_entities[entity_name]

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
