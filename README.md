# Money on Chain Simplified Simulation

This repository contains a very small Python example that mimics a couple of actions from the [Money on Chain](https://github.com/money-on-chain) protocol. It is **only** intended for educational purposes.

The `moc_sim.py` script implements:

- **DoC minting and redemption** using BTC as collateral.
- **BPro minting and redemption**. Each BPro token now reflects the
  proportion of collateral remaining after discounting issued DoC, so its price
  changes as the system evolves.
- A helper method to display the current state of the system.

The initial system state is loaded from `config.json`. Run it with:

```bash
python moc_sim.py  # reads config.json by default
```

The output will show how minting and redeeming affect the internal balances.

## Interactive CLI

You can also launch `moc_ui.py` for an interactive session. It reads the
same configuration file and lets you manually set the BTC price and
advance time steps.

```bash
python moc_ui.py  # optionally pass a different config path
```

Type `help` inside the program to see the available commands.
The UI includes a `panel` command that shows current BTC and token balances,
available DoC to mint, and coverage ratios.

## Historical Simulation

The script `historical_sim.py` runs an automated weekly simulation. It now
reads BTC prices from `btcdata.csv` and samples one row every seven to obtain
weekly prices when the source file contains daily data. You can modify the
script to use a different CSV file if needed. During the run it adjusts the DoC supply so that the
amount available to mint stays at **10%** of the total supply and logs each
step.

```bash
python historical_sim.py
```

At the end of the run it prints the final system summary.

## Educational Example

For a very minimal demonstration, run `educational_example.py`. It executes a few
mint, redeem, and rebalance steps with random BTC prices so you can observe how
the collateral ratio changes.

```bash
python educational_example.py
```
