import numpy as np
import matplotlib.pyplot as plt


# --------------------------
# 1. Define release rules (linear release rules from document)
# --------------------------
def release_team_advisor(month):
    """
    Team & Advisors: 20% = 200M
    - First 12 months locked (month=1..12 => 0)
    - Linear release over next 48 months (month=13..60)
    """
    total = 200_000_000
    lock_months = 12
    linear_months = 48
    if month <= lock_months:
        return 0
    else:
        return total / linear_months


def release_seed(month):
    """
    Seed Round: 10% = 100M
    - First 12 months locked (month=1..12 => 0)
    - Linear release over next 24 months (month=13..36)
    """
    total = 100_000_000
    lock_months = 12
    linear_months = 24
    if month <= lock_months:
        return 0
    elif month <= lock_months + linear_months:
        return total / linear_months
    else:
        return 0


def release_a_round(month):
    """
    A Round & ICO: 5% = 50M
    - First 6 months locked (month=1..6 => 0)
    - Linear release over next 18 months (month=7..24)
    """
    total = 50_000_000
    lock_months = 6
    linear_months = 18
    if month <= lock_months:
        return 0
    elif month <= lock_months + linear_months:
        return total / linear_months
    else:
        return 0


def release_airdrop_liquidity(month):
    """
    Joint Airdrop & Liquidity: 10% = 100M
    - One-time release at TGE, assumed to be in month 1
    """
    total = 100_000_000
    return total if month == 1 else 0


def release_eco_fund(month):
    """
    Ecosystem Fund: 5% = 50M
    - 1% per year for 5 years, total 50M
    - Simplified to fixed monthly release (month=1..60)
    """
    total = 50_000_000
    months_total = 60
    return total / months_total


def release_mining(month):
    """
    Proof of Mining: 5% = 50M
    Simple example:
    - Year 1 (months 1~12) release 30M, 2.5M monthly
    - Year 2 (months 13~24) release 20M, ~1.67M monthly
    - No release after that
    """
    if 1 <= month <= 12:
        return 30_000_000 / 12.0  # ~2.5M
    elif 13 <= month <= 24:
        return 20_000_000 / 12.0  # ~1.67M
    else:
        return 0


def release_early_staking(month):
    """
    Early Staking: 10% = 100M
    - One-time release at TGE, month 1
    """
    total = 100_000_000
    return total if month == 1 else 0


def release_node_staking(month):
    """
    Node Staking Rewards: 30% = 300M
    - Linear release over 5 years, 60 months
    """
    total = 300_000_000
    months_total = 60
    return total / months_total


# --------------------------
# 2. Calculate monthly release amount (1..60)
# --------------------------
months = 60
monthly_mint = []  # Monthly theoretical release amount
categories = {
    "team_advisor": [],
    "seed": [],
    "a_round": [],
    "airdrop_liquidity": [],
    "eco_fund": [],
    "mining": [],
    "early_staking": [],
    "node_staking": [],
}

for m in range(1, months + 1):
    r_team = release_team_advisor(m)
    r_seed = release_seed(m)
    r_a = release_a_round(m)
    r_airdrop = release_airdrop_liquidity(m)
    r_eco = release_eco_fund(m)
    r_mining = release_mining(m)
    r_early_staking = release_early_staking(m)
    r_node = release_node_staking(m)

    # Record release amounts for each category
    categories["team_advisor"].append(r_team)
    categories["seed"].append(r_seed)
    categories["a_round"].append(r_a)
    categories["airdrop_liquidity"].append(r_airdrop)
    categories["eco_fund"].append(r_eco)
    categories["mining"].append(r_mining)
    categories["early_staking"].append(r_early_staking)
    categories["node_staking"].append(r_node)

    monthly_mint.append(r_team + r_seed + r_a + r_airdrop + r_eco + r_mining + r_early_staking + r_node)

# --------------------------
# 3. Simulate supply evolution: Add buyback and burn & leverage based on network income and token price
#
# Assumptions:
# - Fixed monthly network income: 50k, 100k, 5M, 10M USDT
# - Buyback & burn and leverage each use 20% of income, total 40%
# - Token price determined by FDV with total supply of 1B tokens: token_price = FDV / 1e9
# - We simulate three FDV scenarios: downside 5X (60M USDT), baseline (300M USDT), upside 5X (1500M USDT)
#
# Monthly deflation tokens = (monthly_revenue * 0.4) / token_price
#                          = (monthly_revenue * 0.4 * 1e9) / FDV
# --------------------------

# Fixed monthly revenue (USDT)
revenue_scenarios = {
    "500k": 500_000,
    "1M": 1_000_000,
    "5M": 5_000_000,
    "10M": 10_000_000
}

# FDV scenarios (USDT): Down 5X, Baseline, Up 5X
fdv_scenarios = {
    "Down5x": 60e6,  # 60M
    "Baseline": 300e6,  # 300M
    "Up5x": 1500e6  # 1500M
}


def simulate_supply(monthly_revenue, FDV):
    """
    Simulate supply evolution over 60 months:
      Monthly net change = release amount - buyback and burn (including leverage) amount
    Buyback and burn amount calculated based on revenue and FDV:
      deflation_tokens = (monthly_revenue * 0.4 * 1e9) / FDV
    Also calculate monthly "inflation rate" = (net increase / previous month supply) * 100%
    """
    supply = 0.0
    supply_history = []
    inflation_rates = []
    for i in range(months):
        minted = monthly_mint[i]
        deflation_tokens = (monthly_revenue * 0.4 * 1e9) / FDV
        net_change = minted - deflation_tokens
        # If initial supply is 0, set first month inflation to 0 (or handle differently)
        if supply == 0:
            inflation = 0
        else:
            inflation = net_change / supply * 100
        supply += net_change
        supply_history.append(supply)
        inflation_rates.append(inflation)
    return supply_history, inflation_rates


# --------------------------
# 4. Plot monthly inflation rates under different revenue and FDV scenarios
# --------------------------
fig, axes = plt.subplots(len(revenue_scenarios), 1, figsize=(10, 6 * len(revenue_scenarios)))
if len(revenue_scenarios) == 1:
    axes = [axes]

for idx, (rev_label, revenue_val) in enumerate(revenue_scenarios.items()):
    ax = axes[idx]
    for fdv_label, fdv_val in fdv_scenarios.items():
        supply_hist, infl_rates = simulate_supply(revenue_val, fdv_val)
        ax.plot(np.arange(1, months + 1), infl_rates, label=f'FDV: {fdv_label}')
    ax.set_title(f'Monthly Inflation Rate with Monthly Revenue = {rev_label} USDT')
    ax.set_xlabel('Month')
    ax.set_ylabel('Inflation Rate (%)')
    ax.grid(True)
    ax.legend()

plt.tight_layout()
plt.show()

# --------------------------
# 5. Output statistical results: Cumulative release amounts and final supply under example scenarios
# --------------------------
for rev_label, revenue_val in revenue_scenarios.items():
    for fdv_label, fdv_val in fdv_scenarios.items():
        supply_hist, infl_rates = simulate_supply(revenue_val, fdv_val)
        final_supply = supply_hist[-1]
        print(f"Monthly Revenue {rev_label} USDT, FDV {fdv_label}: Final Circulation ≈ {final_supply:.2f} ZB")

print("\nCumulative release amount for each allocation over 5 years (before burn):")
for k, v in categories.items():
    print(f"  {k:20s} => {sum(v):.2f} ZB")