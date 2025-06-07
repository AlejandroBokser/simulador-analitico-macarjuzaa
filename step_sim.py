from moc_sim import StableSystem
from historical_sim import load_price_data, update_price_ma180, adjust_supply


def main(price_file="btcdata.csv", config_file="config.json", weekly=True):
    system = StableSystem.from_config(config_file)
    prices = load_price_data(price_file, weekly=weekly)
    ma_history = [system.price_ma180]
    print("Interactive historical simulation. Press Enter to advance.")
    system.panel()
    for date, price in prices:
        try:
            user = input("\nPress Enter to continue, or 'q' to quit: ").strip().lower()
        except EOFError:
            break
        if user == "q":
            break
        system.set_price(price)
        system.price_ma180 = update_price_ma180(ma_history, price)
        print(f"Date: {date} | BTC Price: {price:.2f} USD")
        system.panel()
        tcov = system.target_coverage()
        delta = adjust_supply(system, tcov)
        if abs(delta) < 1e-9:
            print("No change in DoC supply.")
        elif delta > 0:
            btc_needed = delta / system.price
            print(f"Minted {delta:.2f} DoC adding {btc_needed:.4f} BTC")
        else:
            btc_removed = -delta / system.price
            print(f"Redeemed {-delta:.2f} DoC withdrawing {btc_removed:.4f} BTC")
        system.panel()


if __name__ == "__main__":
    import sys
    price_file = sys.argv[1] if len(sys.argv) > 1 else "btcdata.csv"
    config_file = sys.argv[2] if len(sys.argv) > 2 else "config.json"
    main(price_file, config_file)
