import numpy as np
import matplotlib.pyplot as plt

# ======================================================
# 1. Define Sigmoid Release Function
# ======================================================
def sigmoid_release(total_tokens, total_months, k=0.2):
    """
    Returns an array of length total_months representing monthly token release following a Sigmoid curve.
    Logic:
      - Define Logistic function S(t) = 1 / (1 + exp(-k*(t - mid))) in interval [0, total_months]
      - Normalize to make S(0)=0, S(total_months)=1
      - Monthly release = difference between cumulative release S(t) and S(t-1)
      - Total sum = total_tokens
    Parameters:
      total_tokens: Total tokens to be released over total_months
      total_months: Duration of release in months
      k: Steepness of the curve (higher values concentrate release in the middle period)
    """
    t = np.arange(0, total_months + 1)  # 0..total_months
    mid = total_months / 2.0           # midpoint, can be adjusted as needed

    # Original Logistic function
    raw = 1.0 / (1.0 + np.exp(-k * (t - mid)))
    # Values at t=0 and t=total_months
    start, end = raw[0], raw[-1]

    # Normalize to [0, 1]
    norm = (raw - start) / (end - start)

    # Monthly release = current month cumulative - previous month cumulative
    # Length = total_months
    monthly_fraction = np.diff(norm)
    monthly_release = monthly_fraction * total_tokens
    return monthly_release

# ======================================================
# 2. Define Allocation Rules
# ======================================================
months = 60  # 5 years

def release_team_advisor():
    """
    Team & Advisors: 20% = 200M
    - First 12 months locked
    - Next 48 months with Sigmoid release
    """
    total = 200_000_000
    lock = 12
    release_period = 48

    # Sigmoid distribution over 48 months
    s = sigmoid_release(total, release_period, k=0.2)

    # Create 60-month array: first 12 months=0, next 48 months=s
    arr = np.zeros(months)
    arr[lock:lock+release_period] = s
    return arr

def release_seed():
    """
    Seed Round: 10% = 100M
    - First 12 months locked
    - Next 24 months with Sigmoid release
    """
    total = 100_000_000
    lock = 12
    release_period = 24
    s = sigmoid_release(total, release_period, k=0.2)

    arr = np.zeros(months)
    arr[lock:lock+release_period] = s
    return arr

def release_a_round():
    """
    A Round & ICO: 5% = 50M
    - First 6 months locked
    - Next 18 months with Sigmoid release
    """
    total = 50_000_000
    lock = 6
    release_period = 18
    s = sigmoid_release(total, release_period, k=0.2)

    arr = np.zeros(months)
    arr[lock:lock+release_period] = s
    return arr

def release_airdrop_liquidity():
    """
    Joint Airdrop & Liquidity: 10% = 100M
    - One-time release at TGE (month 1)
    """
    arr = np.zeros(months)
    arr[0] = 100_000_000
    return arr

def release_eco_fund():
    """
    Ecosystem Fund: 5% = 50M
    - Linear over 5 years => 60 months
    """
    arr = np.full(months, 50_000_000 / 60.0)
    return arr

def release_mining():
    """
    Proof of Mining: 5% = 50M (or alternative: Year 1: 3%, Year 2: 2%, Year 3: 1%)
    Demonstration of phased release:
      Year 1 (1..12) release 30M => 2.5M monthly
      Year 2 (13..24) release 20M => 1.67M monthly
      No release after Year 2
    """
    arr = np.zeros(months)
    # Year 1
    arr[0:12] = 30_000_000 / 12.0
    # Year 2
    arr[12:24] = 20_000_000 / 12.0
    return arr

def release_early_staking():
    """
    Early Staking: 10% = 100M
    - One-time release at TGE (month 1)
    """
    arr = np.zeros(months)
    arr[0] = 100_000_000
    return arr

def release_node_staking():
    """
    Node Staking Rewards: 30% = 300M
    - Linear over 5 years => 60 months
    """
    arr = np.full(months, 300_000_000 / 60.0)
    return arr

# ======================================================
# 3. Integrate Monthly Release Amounts
# ======================================================
team_arr = release_team_advisor()
seed_arr = release_seed()
a_round_arr = release_a_round()
airdrop_arr = release_airdrop_liquidity()
eco_arr = release_eco_fund()
mining_arr = release_mining()
early_staking_arr = release_early_staking()
node_staking_arr = release_node_staking()

# Total monthly release
monthly_mint = (team_arr + seed_arr + a_round_arr + airdrop_arr
                + eco_arr + mining_arr + early_staking_arr + node_staking_arr)

# ======================================================
# 4. Deflationary Mechanism: Monthly Buyback + Leverage, 40% of Network Revenue
#    Token price determined by FDV (300M ±5x), Total Supply = 1B
# ======================================================
def simulate_supply(monthly_revenue, FDV):
    """
    Input: Monthly network revenue, FDV
    Output: 60-month supply changes and inflation rates
    - Buyback & burn = monthly_revenue * 0.4 / token_price
                     = (monthly_revenue * 0.4 * 1e9) / FDV
    - Net increase = monthly_mint[i] - buyback_burn
    - Inflation rate = net_increase / previous_month_supply
    """
    supply = 0.0
    supply_history = []
    inflation_rates = []

    for i in range(months):
        minted = monthly_mint[i]
        burn_tokens = (monthly_revenue * 0.4 * 1e9) / FDV  # Monthly burn amount
        net_change = minted - burn_tokens

        if supply == 0:
            inflation = 0
        else:
            inflation = net_change / supply * 100

        supply += net_change
        supply_history.append(supply)
        inflation_rates.append(inflation)

    return supply_history, inflation_rates

# Different revenue and FDV scenarios
revenue_scenarios = {
    "0.5M": 500_000,
    "1M": 1_000_000,
    "5M": 5_000_000,
    "10M": 10_000_000
}
fdv_scenarios = {
    "Down5x": 60e6,      # 60M
    "Baseline": 300e6,   # 300M
    "Up5x": 1500e6       # 1500M
}

# ======================================================
# 5. Plotting: For different revenue scenarios, plot inflation rate curves for 3 FDV scenarios
# ======================================================
fig, axes = plt.subplots(len(revenue_scenarios), 1, figsize=(10, 6 * len(revenue_scenarios)))
axes = axes if isinstance(axes, np.ndarray) else [axes]

for idx, (rev_label, rev_val) in enumerate(revenue_scenarios.items()):
    ax = axes[idx]
    for fdv_label, fdv_val in fdv_scenarios.items():
        supply_hist, infl_rates = simulate_supply(rev_val, fdv_val)
        ax.plot(np.arange(1, months+1), infl_rates, label=f'FDV: {fdv_label}')
    ax.set_title(f"Monthly Network Revenue = {rev_label} USDT, Inflation Rate with Sigmoid(first 3) + Linear Release")
    ax.set_xlabel('Month')
    ax.set_ylabel('Inflation Rate (%)')
    ax.grid(True)
    ax.legend()

plt.tight_layout()
plt.savefig('sigmoid_inflation_rates.png')  # Save the figure
plt.show()

# ======================================================
# 6. Output Example: Final Supply under "Monthly Revenue=1M, FDV=300M" scenario
# ======================================================
# Create a text file to save results
with open('sigmoid_simulation_results.txt', 'w') as f:
    # Write header
    header = "=== Simulation Results for Sigmoid Release Model ===\n\n"
    f.write(header)
    print(header)
    
    # Write results for all scenarios
    for rev_label, rev_val in revenue_scenarios.items():
        for fdv_label, fdv_val in fdv_scenarios.items():
            supply_hist, infl_rates = simulate_supply(rev_val, fdv_val)
            result = f"Monthly Revenue {rev_label} USDT, FDV {fdv_label}: Final Circulation ≈ {supply_hist[-1]:.2f} ZB\n"
            f.write(result)
            print(result, end='')
    
    # Example scenario details
    test_supply, test_infl = simulate_supply(1_000_000, 300e6)
    example = "\n=== Detailed Example: Monthly Revenue=1M USDT, FDV=300M USDT (Baseline) ===\n"
    example += f"  Final circulation at month 60 ≈ {test_supply[-1]:.2f} ZB\n"
    example += f"  Inflation rate at month 60 = {test_infl[-1]:.2f}%\n"
    
    f.write(example)
    print(example)
    
    # Add allocation information
    allocations = {
        "Team & Advisors": sum(team_arr),
        "Seed Round": sum(seed_arr),
        "A Round & ICO": sum(a_round_arr),
        "Airdrop & Liquidity": sum(airdrop_arr),
        "Ecosystem Fund": sum(eco_arr),
        "Proof of Mining": sum(mining_arr),
        "Early Staking": sum(early_staking_arr),
        "Node Staking": sum(node_staking_arr)
    }
    
    f.write("\nCumulative release amount for each allocation over 5 years (before burn):\n")
    print("\nCumulative release amount for each allocation over 5 years (before burn):")
    
    for k, v in allocations.items():
        alloc_info = f"  {k:20s} => {v:.2f} ZB\n"
        f.write(alloc_info)
        print(alloc_info, end='')

print("\nResults have been saved to 'sigmoid_inflation_rates.png' and 'sigmoid_simulation_results.txt'")
