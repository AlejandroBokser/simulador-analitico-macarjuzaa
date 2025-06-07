# Educational demonstration using StableSystem from ``moc_sim.py``
from moc_sim import StableSystem


def rebalance(system: StableSystem, target_ratio: float = 2.0) -> None:
    """Print a simple rebalance suggestion based on current coverage."""

    current_ratio = system.real_coverage()
    print(f"Current collateral ratio: {current_ratio:.2f}")

    btc_price = system.btc_usd_price()
    if current_ratio < target_ratio:
        needed = (target_ratio * system.doc_supply / btc_price) - system.btc_collateral
        print(f"Low collateralization, need ~{needed:.4f} BTC to reach target.")
    elif current_ratio > target_ratio * 1.1:
        excess = system.btc_collateral - (target_ratio * system.doc_supply / btc_price)
        print(
            f"High collateralization, ~{excess:.4f} BTC available to withdraw or mint more DoC."
        )
    else:
        print("Collateralization within desired range.")


if __name__ == "__main__":
    system = StableSystem()
    system.advance_time()
    rebalance(system)
    system.mint_doc(0.2)
    system.advance_time()
    rebalance(system)
    system.redeem_doc(100.0)
    system.advance_time()
    rebalance(system)
