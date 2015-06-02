# EASL 0.3.0
Simulator for an experiment involving artificial infants, and a mobile.

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
