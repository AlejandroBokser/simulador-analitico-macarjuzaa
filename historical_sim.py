import csv
import pandas as pd
from datetime import timedelta
from moc_sim import StableSystem


def load_price_data(path, weekly=False):
    """Load price data from ``path``.

    The function supports files with ``date,price`` or ``Time,BTC`` headers.
    When ``weekly`` is ``True`` only every 7th record is returned so daily
    datasets can be sampled to weekly frequency.
    """

    data = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        # Accept both (date, price) and (Time, BTC) columns
        headers = {h.lower(): h for h in reader.fieldnames}
        date_key = headers.get("date") or headers.get("time")
        price_key = headers.get("price") or headers.get("btc")

        for idx, row in enumerate(reader):
            if weekly and idx % 7 != 0:
                continue
            data.append((row[date_key], float(row[price_key])))
    return data


def update_price_ma180(history, new_price):
    history.append(new_price)
    if len(history) > 26:  # roughly 180 days with weekly data
        history.pop(0)
    return sum(history) / len(history)


def adjust_supply(system, tcov, target_ratio=0.1):
    """Adjust DoC supply so that available to mint is target_ratio of supply."""
    if tcov == 0:
        return 0.0
    target_supply = (system.btc_collateral * system.price / tcov) / (1 + target_ratio)
    delta = target_supply - system.doc_supply
    if abs(delta) < 1e-9:
        return 0.0
    if delta > 0:
        btc_needed = delta / system.price
        system.mint_doc(btc_needed)
    else:
        system.redeem_doc(-delta)
    return delta


def main(
    price_file='btcdata.csv',
    config_file='config.json',
    weekly=True,
):
    system = StableSystem.from_config(config_file)
    prices = load_price_data(price_file, weekly=weekly)
    ma_history = [system.price_ma180]

    for date, price in prices:
        system.set_price(price)
        system.price_ma180 = update_price_ma180(ma_history, price)
        tcov = system.target_coverage()
        change = adjust_supply(system, tcov)
        line = {
            'date': date,
            'price': price,
            'doc_supply': system.doc_supply,
            'btc_collateral': system.btc_collateral,
            'bpro_supply': system.bpro_supply,
            'doc_available': system.doc_available_to_mint(),
            'target_cov': system.target_coverage(),
            'real_cov': system.real_coverage(),
            'change_doc': change,
        }
        print(
            f"{line['date']} Price:{line['price']:.2f} DoC:{line['doc_supply']:.2f} "
            f"BTC:{line['btc_collateral']:.4f} Avail:{line['doc_available']:.2f} "
            f"tCov:{line['target_cov']:.2f} rCov:{line['real_cov']:.2f} "
            f"DeltaDoC:{line['change_doc']:.2f}"
        )

    print("\nFinal State:")
    system.summary()


def run_historical_with_deposit(config_path, price_csv, funding_csv, ma180_csv):
    """Run historical simulation using bucket deposit logic."""
    system = StableSystem.from_config(config_path)

    price_df = pd.read_csv(price_csv, parse_dates=['Time'])
    price_df['date'] = price_df['Time'].dt.floor('D')

    funding_df = pd.read_csv(funding_csv, parse_dates=['date'])

    ma180_df = pd.read_csv(ma180_csv, parse_dates=['date']).set_index('date')

    dates = sorted(price_df['date'].unique())
    for current_date in dates:
        price_usd = price_df.loc[price_df['date'] == current_date, 'BTC'].iloc[-1]
        row = funding_df.loc[funding_df['date'] == current_date]
        if not row.empty:
            funding_rate = float(row['funding_rate_daily'].iloc[0])
        else:
            funding_rate = 0.0
        system.current_price_usd = price_usd
        system.step_one_day(
            current_date=current_date,
            current_price=price_usd,
            historical_ma180_df=ma180_df,
            funding_rate_market=funding_rate,
        )

    print("=== Resultados finales ===")
    print(f"  DoC en vault_deposit: {system.vault_docs:.4f}")
    print(f"  DoC totales emitidos:  {system.doc_supply:.4f}")
    print(f"  BTC en colateral:      {system.btc_collateral:.6f}")


if __name__ == '__main__':
    run_historical_with_deposit(
        config_path='config.json',
        price_csv='btcdata.csv',
        funding_csv='merged_btc_funding.csv',
        ma180_csv='btc_ma180.csv',
    )
