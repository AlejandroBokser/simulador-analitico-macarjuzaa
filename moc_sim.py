import json
import random

class StableSystem:
    def __init__(
        self,
        btc_collateral=100.0,
        doc_supply=50.0,
        bpro_supply=0.0,
        price=25000.0,
        time=0,
        param_coverage=2.0,
        price_ma180=25000.0,
        price_ema=None,
        ema_alpha=0.1,
        doc_threshold=90.0,
        vault_docs=0.0,
    ):
        self.btc_collateral = btc_collateral
        self.doc_supply = doc_supply
        self.bpro_supply = bpro_supply
        self.price = price
        self.time = time
        self.param_coverage = param_coverage
        self.price_ma180 = price_ma180
        self.ema_alpha = ema_alpha
        self.price_ema = price_ema if price_ema is not None else price
        self.doc_threshold = doc_threshold
        self.vault_docs = vault_docs
        self.current_price_usd = price

    @classmethod
    def from_config(cls, filename: str):
        with open(filename) as f:
            data = json.load(f)
        return cls(
            btc_collateral=data.get("btc_collateral", 0.0),
            doc_supply=data.get("doc_supply", 0.0),
            bpro_supply=data.get("bpro_supply", 0.0),
            price=data.get("btc_price", 0.0),
            param_coverage=data.get(
                "param_coverage",
                data.get("coverage_param", data.get("target_parameter", 0.0)),
            ),
            price_ma180=data.get(
                "price_ma180",
                data.get("average_180d", data.get("price_average_180d", 0.0)),
            ),
            price_ema=data.get("price_ema"),
            ema_alpha=data.get("ema_alpha", 0.1),
            doc_threshold=data.get("simulation_parameters", {}).get("doc_threshold", 90),
        )

    def btc_usd_price(self):
        return self.price

    def target_coverage(self):
        """Return the target collateral coverage without a minimum cap."""
        if self.price_ma180 == 0:
            return 0.0
        return 1 + (self.price / self.price_ma180) * (self.param_coverage - 1)

    def set_price(self, new_price: float):
        """Manually set the BTC price."""
        self.price = new_price
        self.price_ema = self.ema_alpha * new_price + (1 - self.ema_alpha) * self.price_ema
        print(f"BTC price set to {self.price:.2f} USD")

    def advance_time(self, steps: int = 1):
        """Advance time and apply a random walk to the BTC price."""
        for _ in range(steps):
            variation = random.uniform(-0.05, 0.05) * self.price
            self.price += variation
            self.price_ema = self.ema_alpha * self.price + (1 - self.ema_alpha) * self.price_ema
            self.time += 1
        print(
            f"Advanced time by {steps} units. BTC price is now {self.price:.2f} USD"
        )

    def mint_doc(self, btc_amount):
        btc_price = self.btc_usd_price()
        self.btc_collateral += btc_amount
        doc_minted = btc_price * btc_amount
        self.doc_supply += doc_minted
        print(f"Minted {doc_minted:.2f} DoC with {btc_amount:.4f} BTC at {btc_price:.2f} USD/BTC")

    def mint_doc_amount(self, doc_amount):
        """Mint a specific amount of DoC calculating the required BTC."""
        btc_price = self.btc_usd_price()
        btc_needed = doc_amount / btc_price
        self.btc_collateral += btc_needed
        self.doc_supply += doc_amount
        print(
            f"Minted {doc_amount:.2f} DoC with {btc_needed:.4f} BTC at {btc_price:.2f} USD/BTC"
        )

    def redeem_doc(self, doc_amount):
        if doc_amount > self.doc_supply:
            raise ValueError("Not enough DoC tokens to redeem")
        btc_price = self.btc_usd_price()
        btc_returned = doc_amount / btc_price
        self.doc_supply -= doc_amount
        self.btc_collateral -= btc_returned
        print(
            f"Redeemed {doc_amount:.2f} DoC for {btc_returned:.4f} BTC at {btc_price:.2f} USD/BTC"
        )

    def mint_bpro(self, btc_amount):
        self.btc_collateral += btc_amount
        self.bpro_supply += btc_amount
        print(f"Minted {btc_amount:.4f} BPro with {btc_amount:.4f} BTC")

    def redeem_bpro(self, bpro_amount):
        if bpro_amount > self.bpro_supply:
            raise ValueError("Not enough BPro tokens to redeem")
        self.bpro_supply -= bpro_amount
        self.btc_collateral -= bpro_amount
        print(f"Redeemed {bpro_amount:.4f} BPro for {bpro_amount:.4f} BTC")

    def real_coverage(self):
        """Current collateral coverage."""
        if self.doc_supply == 0:
            return float("inf")
        return (self.btc_collateral * self.price) / self.doc_supply

    def leverage(self):
        """Return the BPro leverage based on real coverage."""
        rcov = self.real_coverage()
        if rcov == float("inf"):
            return 1.0
        if rcov <= 1:
            return 0.0
        return rcov / (rcov - 1)

    def bpro_price(self):
        """Return the current BPro price in USD."""
        collateral_value = self.btc_collateral * self.price
        if self.bpro_supply == 0:
            return 0.0
        return (collateral_value - self.doc_supply) / self.bpro_supply

    def bpro_price_btc(self):
        """Return the current BPro price in BTC."""
        if self.price == 0:
            return 0.0
        return self.bpro_price() / self.price

    def doc_available_to_mint(self):
        """Return the amount of DoC that could be minted while keeping target coverage."""
        tcov = self.target_coverage()
        if tcov == 0:
            return 0.0
        max_doc = (self.btc_collateral * self.price) / tcov
        return max(0.0, max_doc - self.doc_supply)

    def price_ma180_four_years_ago(self, historical_ma180_df, current_date):
        """Return ma180 value from four years before current_date."""
        from datetime import timedelta

        target_date = current_date - timedelta(days=365 * 4)
        past_rows = historical_ma180_df.loc[:target_date]
        if past_rows.empty:
            return float(historical_ma180_df["ma180"].iloc[0])
        return float(past_rows["ma180"].iloc[-1])

    def compute_daily_doc_rate(self, ma_current, ma_past):
        """Compute the maximum daily DoC interest rate."""
        years = 4 * 365
        if ma_past <= 0:
            return 0.0
        total_factor = ma_current / ma_past
        if total_factor <= 0.0:
            return 0.0
        daily_growth = total_factor ** (1.0 / years) - 1.0
        return daily_growth / 4.0

    def mint_docs_for_deposit(self, quantity_docs):
        """Mint DoC using collateral and deposit them into the vault."""
        price_usd = self.current_price_usd
        btc_needed = quantity_docs / price_usd
        if btc_needed > self.btc_collateral:
            quantity_docs = self.btc_collateral * price_usd
            btc_needed = self.btc_collateral
        self.btc_collateral -= btc_needed
        self.doc_supply += quantity_docs
        self.vault_docs += quantity_docs

    def redeem_docs_from_deposit(self, quantity_docs):
        """Redeem DoC from the deposit vault and return BTC collateral."""
        price_usd = self.current_price_usd
        btc_returned = quantity_docs / price_usd
        self.vault_docs -= quantity_docs
        self.doc_supply -= quantity_docs
        self.btc_collateral += btc_returned

    def step_one_day(self, current_date, current_price, historical_ma180_df, funding_rate_market):
        """Execute one day of simulation including bucket deposit logic."""
        # 1) Previous logic: adjust DoC supply based on target coverage
        self.set_price(current_price)
        tcov = self.target_coverage()
        self.adjust_doc_supply(tcov)

        docs_disp = self.doc_available_to_mint()
        docs_emitidos = self.doc_supply
        percent_doc = 0.0
        if (docs_emitidos + docs_disp) > 0:
            percent_doc = docs_disp / (docs_emitidos + docs_disp)

        # --------------------------------------------------
        # Split remaining emission between protocol and user
        protocolaDocs = docs_disp * percent_doc
        userDocs = docs_disp - protocolaDocs
        if userDocs > 1e-9:
            btcNeededUser = userDocs / self.price
            self.mint_doc(btcNeededUser)
            self.vault_docs += userDocs

        # 2) Moving averages
        ma_current = float(historical_ma180_df.loc[current_date, "ma180"])
        ma_past = self.price_ma180_four_years_ago(historical_ma180_df, current_date)

        # 3) Maximum daily rate
        rate_max = self.compute_daily_doc_rate(ma_current, ma_past)

        # 4) Apply threshold
        if self.doc_supply < self.doc_threshold:
            applied_rate = rate_max
        else:
            applied_rate = 0.0

        # 5) Compare vs. market funding rate
        delta_rate = applied_rate - funding_rate_market
        if delta_rate > 0:
            new_docs = delta_rate * self.doc_supply
            self.mint_docs_for_deposit(new_docs)
        elif delta_rate < 0 and self.vault_docs > 0:
            withdraw_docs = min(self.vault_docs, abs(delta_rate) * self.vault_docs)
            self.redeem_docs_from_deposit(withdraw_docs)

        # 6) Pay daily interest
        interest_docs = applied_rate * self.doc_supply
        if interest_docs > 0:
            self.mint_docs_for_deposit(interest_docs)

        # Update price_ma180 for future target coverage
        self.price_ma180 = ma_current

    def adjust_doc_supply(self, tcov, target_ratio=0.1):
        """Adjust DoC supply so that available to mint is target_ratio of supply."""
        if tcov == 0:
            return 0.0
        target_supply = (self.btc_collateral * self.price / tcov) / (1 + target_ratio)
        delta = target_supply - self.doc_supply
        if abs(delta) < 1e-9:
            return 0.0
        if delta > 0:
            self.mint_docs_for_deposit(delta)
        else:
            self.redeem_docs_from_deposit(-delta)
        return delta

    def panel(self):
        """Display a compact panel of the system state."""
        print("=== System Panel ===")
        print(f"BTC Collateral: {self.btc_collateral:.4f} BTC")
        bpro_usd = self.bpro_price()
        print(f"BPro Supply: {self.bpro_supply:.4f} BPro (Price {bpro_usd:.2f} USD)")
        print(f"BPro Price BTC: {self.bpro_price_btc():.4f} BTC/BPro")
        print(f"DoC Supply: {self.doc_supply:.2f} DoC")
        print(f"DoC Available to Mint: {self.doc_available_to_mint():.2f} DoC")
        print(f"Price EMA: {self.price_ema:.2f} USD")
        print(f"Target Coverage: {self.target_coverage():.2f}")
        print(f"Real Coverage: {self.real_coverage():.2f}")
        print(f"Leverage: {self.leverage():.2f}")
        print("====================")

    def summary(self):
        price = self.btc_usd_price()
        collateral_value = price * self.btc_collateral
        print("--- System Summary ---")
        print(f"Time: {self.time}")
        print(f"BTC Collateral: {self.btc_collateral:.4f} BTC")
        print(f"Collateral Value: {collateral_value:.2f} USD (Price {price:.2f} USD/BTC)")
        print(f"180d Average Price: {self.price_ma180:.2f} USD")
        print(f"Price EMA: {self.price_ema:.2f} USD")
        print(f"Parameter Coverage: {self.param_coverage:.2f}")
        print(f"Target Coverage: {self.target_coverage():.2f}")
        print(f"Leverage: {self.leverage():.2f}")
        print(f"DoC Supply: {self.doc_supply:.2f} DoC")
        print(f"BPro Supply: {self.bpro_supply:.4f} BPro")
        print(f"BPro Price: {self.bpro_price():.2f} USD ({self.bpro_price_btc():.4f} BTC/BPro)")
        bpro_value_btc = self.bpro_price_btc() * self.bpro_supply
        print(f"BPro Value: {bpro_value_btc:.4f} BTC")
        print("-----------------------")

if __name__ == "__main__":
    try:
        system = StableSystem.from_config("config.json")
    except FileNotFoundError:
        system = StableSystem()
    system.summary()

    system.mint_doc(0.1)
    system.mint_bpro(0.2)
    system.advance_time()
    system.summary()

    system.set_price(30000)
    system.redeem_doc(5.0)
    system.redeem_bpro(0.1)
    system.summary()
