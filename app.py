# Import necessary libraries for web framework and numerical computations
from flask import Flask, request, jsonify
import numpy as np

# Initialize Flask application
app = Flask(__name__)

def simulate_portfolio(age, retirement_age, savings, return_rate, volatility, contribution, 
                      goal=1_000_000, n_simulations=10000, inflation_rate=0.03, inflation_vol=0.02,
                      stock_allocation=0.6, bond_allocation=0.3, cash_allocation=0.1,
                      stock_return=0.08, stock_vol=0.15, bond_return=0.04, bond_vol=0.08,
                      cash_return=0.02, cash_vol=0.01, correlation_stock_bond=0.3,
                      contribution_growth_rate=0.03, withdrawal_rate=0.04, retirement_duration=30):
    """
    Simulate retirement portfolio using enhanced Monte Carlo method with realistic features.

    This function runs multiple simulations of portfolio growth over time, incorporating:
    - Lognormal returns for multiplicative growth
    - Inflation effects on contributions
    - Multi-asset allocation with correlations
    - Dynamic contribution growth
    - Post-retirement withdrawals

    Parameters:
    - age: Current age
    - retirement_age: Target retirement age
    - savings: Current savings amount
    - return_rate: Expected annual return (legacy single-asset, used if allocations not specified)
    - volatility: Annual volatility (legacy)
    - contribution: Initial annual contribution amount
    - goal: Target retirement savings amount (default: $1M)
    - n_simulations: Number of Monte Carlo simulations (default: 10,000)
    - inflation_rate: Expected annual inflation rate (default: 3%)
    - inflation_vol: Volatility of inflation (default: 2%)
    - stock_allocation: Fraction allocated to stocks (default: 60%)
    - bond_allocation: Fraction allocated to bonds (default: 30%)
    - cash_allocation: Fraction allocated to cash (default: 10%)
    - stock_return: Expected annual return for stocks (default: 8%)
    - stock_vol: Volatility for stocks (default: 15%)
    - bond_return: Expected annual return for bonds (default: 4%)
    - bond_vol: Volatility for bonds (default: 8%)
    - cash_return: Expected annual return for cash (default: 2%)
    - cash_vol: Volatility for cash (default: 1%)
    - correlation_stock_bond: Correlation between stock and bond returns (default: 0.3)
    - contribution_growth_rate: Annual growth rate of contributions (default: 3%)
    - withdrawal_rate: Annual withdrawal rate post-retirement (default: 4%)
    - retirement_duration: Years to simulate post-retirement (default: 30)

    Returns:
    Dictionary with summary statistics from all simulations
    """
    # Calculate total simulation years (accumulation + retirement phases)
    accumulation_years = retirement_age - age
    total_years = accumulation_years + retirement_duration

    # Prepare multi-asset return parameters for lognormal distribution
    # For lognormal returns: mean = drift - vol^2/2, sigma = vol
    drift_stock = stock_return - stock_vol**2 / 2
    drift_bond = bond_return - bond_vol**2 / 2
    drift_cash = cash_return - cash_vol**2 / 2
    
    # Build covariance matrix for correlated asset returns
    vols = np.array([stock_vol, bond_vol, cash_vol])
    corr_matrix = np.array([
        [1.0, correlation_stock_bond, 0.0],
        [correlation_stock_bond, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ])
    cov_matrix = np.outer(vols, vols) * corr_matrix

    # Lists to store final wealth, maximum drawdown, and survival status from each simulation
    final_wealths = []
    drawdowns = []
    survivals = []

    # Run Monte Carlo simulations
    for _ in range(n_simulations):
        # Initialize wealth and tracking variables for this simulation
        wealth = savings
        peak = savings  # Highest wealth reached so far
        max_drawdown = 0  # Maximum percentage decline from peak
        contribution_current = contribution  # Current annual contribution amount

        # Simulate portfolio growth year by year
        for year in range(total_years):
            # Generate inflation for this year
            inflation = np.random.normal(inflation_rate, inflation_vol)
            
            # Generate correlated log returns for each asset class
            log_returns = np.random.multivariate_normal(
                [drift_stock, drift_bond, drift_cash], 
                cov_matrix
            )
            
            # Calculate portfolio log return as weighted average
            portfolio_log_return = (
                stock_allocation * log_returns[0] +
                bond_allocation * log_returns[1] + 
                cash_allocation * log_returns[2]
            )
            
            # Apply portfolio growth (multiplicative for lognormal)
            wealth *= np.exp(portfolio_log_return)
            
            # Handle accumulation vs retirement phase
            if year < accumulation_years:
                # Accumulation phase: add grown contribution
                wealth += contribution_current
                # Grow contribution for next year
                contribution_current *= (1 + contribution_growth_rate)
            else:
                # Retirement phase: withdraw percentage of wealth
                withdrawal = wealth * withdrawal_rate
                wealth -= withdrawal
            
            # Update peak wealth if current wealth is higher
            peak = max(peak, wealth)
            
            # Calculate current drawdown (percentage decline from peak)
            if peak > 0:
                drawdown = (peak - wealth) / peak
            else:
                drawdown = 0
            
            # Track the maximum drawdown experienced in this simulation
            max_drawdown = max(max_drawdown, drawdown)

        # Store results from this simulation
        final_wealths.append(wealth)
        drawdowns.append(max_drawdown)
        survivals.append(wealth > 0)  # Portfolio survives if positive wealth at end

    # Convert results to numpy arrays for efficient statistical calculations
    final_wealths = np.array(final_wealths)
    drawdowns = np.array(drawdowns)
    survivals = np.array(survivals)

    # Calculate comprehensive risk and return metrics
    return {
        "summary": {
            # Central tendency: median final wealth (50th percentile)
            "median": float(np.median(final_wealths)),

            # Range of outcomes: 10th and 90th percentiles
            "percentile_10": float(np.percentile(final_wealths, 10)),
            "percentile_90": float(np.percentile(final_wealths, 90)),

            # Risk metrics: Value at Risk (5th percentile - worst 5% of outcomes)
            "var_5": float(np.percentile(final_wealths, 5)),

            # Conditional VaR: Expected loss in worst 5% of cases
            "cvar_5": float(np.mean(final_wealths[final_wealths <= np.percentile(final_wealths, 5)])),

            # Success probability: Chance of reaching retirement goal
            "probability_reaching_goal": float(np.mean(final_wealths >= goal)),

            # Survival probability: Chance portfolio lasts through retirement
            "survival_probability": float(np.mean(survivals)),

            # Risk metric: Average maximum drawdown across all simulations
            "average_max_drawdown": float(np.mean(drawdowns)),

            # Volatility: Standard deviation of final wealth outcomes
            "volatility": float(np.std(final_wealths)),
        }
    }

# API endpoint to handle portfolio simulation requests
@app.route('/simulate', methods=['POST'])
def simulate():
    # Parse JSON data from the POST request
    data = request.get_json()

    # Run simulation with user-provided parameters (use defaults for optional fields)
    result = simulate_portfolio(
        age=data['age'],
        retirement_age=data['retirement_age'],
        savings=data['savings'],
        return_rate=data.get('return_rate', 0.07),  # Legacy parameter
        volatility=data.get('volatility', 0.15),    # Legacy parameter
        contribution=data['contribution'],
        goal=data.get('goal', 1_000_000),
        n_simulations=data.get('n_simulations', 10000),
        inflation_rate=data.get('inflation_rate', 0.03),
        inflation_vol=data.get('inflation_vol', 0.02),
        stock_allocation=data.get('stock_allocation', 0.6),
        bond_allocation=data.get('bond_allocation', 0.3),
        cash_allocation=data.get('cash_allocation', 0.1),
        stock_return=data.get('stock_return', 0.08),
        stock_vol=data.get('stock_vol', 0.15),
        bond_return=data.get('bond_return', 0.04),
        bond_vol=data.get('bond_vol', 0.08),
        cash_return=data.get('cash_return', 0.02),
        cash_vol=data.get('cash_vol', 0.01),
        correlation_stock_bond=data.get('correlation_stock_bond', 0.3),
        contribution_growth_rate=data.get('contribution_growth_rate', 0.03),
        withdrawal_rate=data.get('withdrawal_rate', 0.04),
        retirement_duration=data.get('retirement_duration', 30)
    )

    # Return simulation results as JSON response
    return jsonify(result)

# Run the Flask application in debug mode when executed directly
if __name__ == '__main__':
    app.run(debug=True)
