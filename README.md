# FIRE Monte Carlo simulator

Simulates outcomes of VWRP and 60/40 equity/bond mix over period with following params:

 * Yearly withdrawal amount is constant, reducing at a fixed age
 * Inheritance occurs as lump sum at fixed age
 * State pension begins at fixed age

Variables configurable in `config.json`

## Running
```
sudo docker compose run --rm fire_simulator

OR

./run.sh
```
