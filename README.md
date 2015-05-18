# EASL
Simulator for an experiment involving artificial infants, and a mobile.

## Creating a simulation
To create a new simulation, first 

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
