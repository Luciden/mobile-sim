# EASL 0.5.0
Simulator for an experiment involving artificial infants, and a mobile.

## Running simulations with the Simulation Suite
(Some parts are still sort of hacked together, but the examples should
clarify some, I think.)

In `mobile-world.py` in the `"__main__"` section at the end of the file,
simulation configurations can be configured and the simulator can be set
to run either all, or a single, simulation of these configurations.

First, a set of configurations has to be described, which is done by
creating a SimulationSuite.

```python
ss = SimulationSuite()
```

Because it might be useful to see what is happening during the simulation,
a Visualizer can be configured, such as the PyGameVisualizer (the only one
available for now, see the section on the PyGameVisualizer for keyboard
shortcuts).

```python
ss.set_visualizer(PyGameVisualizer())
```

The length of the simulation, in number of iterations, can be set.
For data output purposes, the number of bins that are used to group
the data can also be changed.

```python
ss.set_simulation_length(240)
ss.set_data_bins(6) # Will in this case make 20 bins of length 6 to use in outputting a .csv file
```

For the actual simulation setup, entities can be added.
Because some experimental setups contain the same components (entities, controllers, triggers),
all components can be added either as 'constant' (i.e. in all simulations) or as 'conditional'
(i.e. only in certain conditions).

For the constant entities:

```python
# A dictionary of name: Entity
# Here create_infant and create_mobile_direction are functions that return an Entity
ss.add_constant_entities({"infant": create_infant, "mobile": create_mobile_direction})
```

And similarly for the controllers:

```python
# For a specific entity (given by the name)
#   Specify controllers that can be identified by a name
# Here infant_simple_controller and infant_causal_controller are functions that return a Controller
ss.add_controllers("infant", {"simple": infant_simple_controller, "causal": infant_causal_controller})
```

And then similarly for triggers.
Triggers describe how entities in the world are connected (such as a babybot's right foot being
connected to a mobile) and can be added/removed at certain iterations.

Triggers are added for a specific 'experimental condition' (identified by a name), so that these conditions can
be identified.

For example, to add a link between an infant's right foot and a mobile's movement:

```python
ss.add_initial_triggers({"experimental": [("infant", "right-foot-position", "movement", "mobile")]})
```

Similarly for trigger changes, but now next to the condition's name, the number of the iteration also has
to be specified.

```python
ss.add_conditional_trigger_changes({"experimental": {"plain": ([], []),
                                                         "remove_halfway": ({60: [("infant", "left-hand-position", "movement", "mobile")]},
                                                                            {60: [("infant", "right-foot-position", "movement", "mobile")]})}})
```

To make comma-separated value files of data, the entity attributes's names should be specified with
a name for the column in the data file.
It is made specifically with the mobile experiment in mind (i.e. it looks for changes in actual limb position during the experiment).

For example, the following will make the data for all limbs and create 2 files:
one file with the raw data that specifies a 1 if the limb's position changed and a 0 if it did not,
and one file where these values are summed into bins.
Both files are named with the controller's and condition's names, so that they can easily be identified.
An example filename is `experimental-plain-infant-causal.csv` or `experimental-plain-infant-causal_bins.csv`.

```python
ss.add_constant_data_collection(["left-hand-position", "right-hand-position", "left-foot-position", "right-foot-position"], ["lh", "rh", "lf", "rf"])
```

Setting `run_single` to `True` will run the simulation with the given
parameters.

For example,

```python
ss.run_single("experimental", "remove_halfway", {"infant": "causal"})
```

will run the condition (i.e. the set-up of which entities are present) with the infant and mobile,
with the trigger changes of the "remove_halfway" trigger condition, which will change the limb's position
from the right foot to the left hand,
with the infant's controller being a causal learning controller.

Possible controllers:

- `causal`: the 'causal learning' controller with Gopnik's algorithm
- `simple`: the operant conditioning controller that changes the probability distribution
- `operant` (deprecated): the 'operant conditioning' controller using the algorithm by Touretzky et al.
- `random`: a controller that samples motor signals at random

## PyGameVisualizer keyboard controls

### Pausing etc.

- `space`: pause/unpause the simulation
- `s`: simulate for 1 iteration, then pause

### Simulation speed

See `dt` in the top-left corner of the simulator screen.

- `up`: increase the delay between iterations by 100 ms
- `down`: decrease the delay between iterations by 100 ms

### Changing limbs connected to the mobile

Connections between the infant's limbs and the mobile can be added/removed.

- `1`: select the `left hand`
- `2`: select the `right hand`
- `3`: select the `left foot`
- `4`: select the `right foot`

The following commands work with the currently selected limb (displayed in the
top-left corner)

- `= (+)`: add a link between the mobile and the currently selected limb
- `-`: remove the link between the mobile and the currently selected limb (if any)
- `0`: remove links between all limbs and the mobile and add a link with the currently selected limb

## Creating a simulation
Describing a simulation consists of three parts:

1. Initializing the description;
2. Describing the entities that are in the world
3. Describing the controllers that determine how entities behave

### Initializing the description
This is done simply by creating a new `World`.

```python
world = World()
```

### Creating entities
Initialize the entity, by giving it a name that it will be identified by when
connecting entities.

```python
example = Entity("example")
```

Assign attributes:

1. Attribute name. This is any string.
2. Initial value. Any value that occurs in the list of possible values described
next.
3. List of possible values. These can be any kind of value, but are typically
strings.
4. Function `f(old, new) : string, {}`. For any pair of old and new values,
describes what event (a name and its parameters) fires, if any.

```python
example.add_attribute("name", "x", ["x", "y"], lambda: None)
```

Describing actions:

1. name
2. values
3. default value
4. Function `f(self) : None`. Describes how the entity's attributes change when
the action is performed. Should change values by calling
`self.try_change(name, value)` and get values by `self.a[attribute]`.

```python
example.add_action("action", ["left", "right"], "left", lambda self: self.a["name"] = "y")
```

## Running the simulation

Once the world description, say `world` is finished, the simulation is run by
calling `run(n)`, which runs the simulation for `n` iterations.

```python
world.run(10)
```

This results in a `Log`, which can be visualized using PyGame:

```python
log = world.run(10)

v = Visualizer()
v.visualize(log)
```
