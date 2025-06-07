#!/usr/bin/env python3
"""Generate a CSV log with system metrics for each BTC price."""
import csv
import sys
import contextlib
import os

from moc_sim import StableSystem
from historical_sim import load_price_data, update_price_ma180, adjust_supply


def main(price_file='btcdata.csv', config_file='config.json', output_file='output.csv', weekly=True):
    system = StableSystem.from_config(config_file)
    prices = load_price_data(price_file, weekly=weekly)
    ma_history = [system.price_ma180]

    fields = [
        'precio_btc',
        'media',
        'btc_en_el_protocolo',
        'cantidad_bpros',
        'doc_emitidos',
        'docs_disponibles_para_emitir',
        'leverage',
        'cobertura_objetivo',
        'cobertura_real',
        'precio_bpro',
    ]

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for _date, price in prices:
            with open(os.devnull, 'w') as devnull, contextlib.redirect_stdout(devnull):
                system.set_price(price)
                system.price_ma180 = update_price_ma180(ma_history, price)
                tcov = system.target_coverage()
                adjust_supply(system, tcov)
            writer.writerow({
                'precio_btc': system.price,
                'media': system.price_ma180,
                'btc_en_el_protocolo': system.btc_collateral,
                'cantidad_bpros': system.bpro_supply,
                'doc_emitidos': system.doc_supply,
                'docs_disponibles_para_emitir': system.doc_available_to_mint(),
                'leverage': system.leverage(),
                'cobertura_objetivo': system.target_coverage(),
                'cobertura_real': system.real_coverage(),
                'precio_bpro': system.bpro_price(),
            })


if __name__ == '__main__':
    price_file = sys.argv[1] if len(sys.argv) > 1 else 'btcdata.csv'
    config_file = sys.argv[2] if len(sys.argv) > 2 else 'config.json'
    output_file = sys.argv[3] if len(sys.argv) > 3 else 'output.csv'
    main(price_file, config_file, output_file)
