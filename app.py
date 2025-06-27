from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

def simulate_portfolio(
    age, retirement_age, savings, return_rate,
    volatility, contribution, goal, num_simulations
):
    years = retirement_age - age
    final_balances = []
    wealth_paths = []

    for _ in range(num_simulations):
        balance = savings
        path = [balance]

        # Log-normal returns: more realistic than normal
        mu = np.log(1 + return_rate) - 0.5 * volatility**2
        yearly_returns = np.random.lognormal(mean=mu, sigma=volatility, size=years)

        for r in yearly_returns:
            balance = balance * r + contribution
            path.append(balance)

        wealth_paths.append(path)
        final_balances.append(path[-1])

    # Convert to NumPy array for easier stats
    final_balances = np.array(final_balances)
    wealth_paths = np.array(wealth_paths)  # shape: (simulations, years+1)

    # Summary stats
    summary = {
        "median": round(np.median(final_balances), 2),
        "percentile_10": round(np.percentile(final_balances, 10), 2),
        "percentile_90": round(np.percentile(final_balances, 90), 2),
        "var_5": round(np.percentile(final_balances, 5), 2),
        "cvar_5": round(np.mean(final_balances[final_balances <= np.percentile(final_balances, 5)]), 2),
        "volatility": round(np.std(final_balances), 4),
        "goal_probability": round(np.mean(final_balances >= goal), 4),
    }

    # Max drawdown (average of worst drawdowns across simulations)
    drawdowns = []
    for path in wealth_paths:
        peak = path[0]
        max_dd = 0
        for value in path:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        drawdowns.append(max_dd)
    summary["max_drawdown"] = round(np.mean(drawdowns), 4)

    # Wealth percentiles by year (for charting)
    wealth_percentiles = {}
    for t in range(wealth_paths.shape[1]):
        wealth_percentiles[f"year_{t}"] = {
            "p10": round(np.percentile(wealth_paths[:, t], 10), 2),
            "p50": round(np.percentile(wealth_paths[:, t], 50), 2),
            "p90": round(np.percentile(wealth_paths[:, t], 90), 2),
        }

    return {
        "summary": summary,
        "wealth_percentiles": wealth_percentiles,
        "metadata": {
            "num_simulations": num_simulations,
            "years": years
        }
    }

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()

    # Get and validate all required inputs
    age = int(data.get('age'))
    retirement_age = int(data.get('retirement_age'))
    savings = float(data.get('savings'))
    return_rate = float(data.get('return_rate'))
    volatility = float(data.get('volatility'))
    contribution = float(data.get('contribution'))
    goal = float(data.get('goal', 1_000_000))
    num_simulations = int(data.get('num_simulations', 10000))

    result = simulate_portfolio(
        age, retirement_age, savings, return_rate,
        volatility, contribution, goal, num_simulations
    )

    return jsonify(result)

@app.route('/')
def home():
    return "<h1>Welcome to the Capital Forecast Simulator API ⭐️</h1>"

if __name__ == '__main__':
    app.run(debug=True)
