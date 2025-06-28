from flask import Flask, request, jsonify
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/simulate": {"origins": "*"}}, methods=["POST"])

@app.route('/')
def home():
    return "Retirement Monte Carlo Simulation API"

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()

    # Inputs
    age = data.get('age')
    retirement_age = data.get('retirement_age')
    savings = data.get('savings')
    return_rate = data.get('return_rate')
    volatility = data.get('volatility')
    contribution = data.get('contribution')
    risk_tolerance = data.get('risk_tolerance')
    inflation_rate = data.get('inflation_rate')
    wealth_goal = data.get('wealth_goal')

    years = retirement_age - age
    num_simulations = 10000
    adjusted_returns = []

    # Modify return/volatility based on risk tolerance
    if risk_tolerance == "conservative":
        return_rate -= 0.01
        volatility *= 0.75
    elif risk_tolerance == "aggressive":
        return_rate += 0.01
        volatility *= 1.25
    # Adjust for inflation
    real_return_rate = return_rate - inflation_rate

    all_simulations = []
    wealth_over_time = {f"year_{i}": [] for i in range(years + 1)}

    for _ in range(num_simulations):
        balance = savings
        path = [balance]
        yearly_returns = np.random.normal(real_return_rate, volatility, years)

        for r in yearly_returns:
            balance = balance * (1 + r) + contribution
            path.append(balance)

        for i, val in enumerate(path):
            wealth_over_time[f"year_{i}"].append(val)

        all_simulations.append(path)

    final_values = [sim[-1] for sim in all_simulations]
    wealth_percentiles = {
        f"year_{i}": {
            "p10": round(np.percentile(wealth_over_time[f"year_{i}"], 10), 2),
            "p50": round(np.percentile(wealth_over_time[f"year_{i}"], 50), 2),
            "p90": round(np.percentile(wealth_over_time[f"year_{i}"], 90), 2)
        } for i in range(years + 1)
    }

    # Risk metrics
    sorted_final = np.sort(final_values)
    var_5 = round(np.percentile(sorted_final, 5), 2)
    cvar_5 = round(np.mean(sorted_final[:int(0.05 * num_simulations)]), 2)
    max_drawdowns = []

    for path in all_simulations:
        peak = path[0]
        max_dd = 0
        for val in path:
            if val > peak:
                peak = val
            dd = (peak - val) / peak
            max_dd = max(max_dd, dd)
        max_drawdowns.append(max_dd)

    goal_prob = round(sum(val >= wealth_goal for val in final_values) / num_simulations, 4)

    summary = {
        "median": round(np.median(final_values), 2),
        "percentile_10": round(np.percentile(final_values, 10), 2),
        "percentile_90": round(np.percentile(final_values, 90), 2),
        "volatility": round(np.std(final_values), 2),
        "var_5": var_5,
        "cvar_5": cvar_5,
        "max_drawdown": round(np.mean(max_drawdowns), 4),
        "goal_probability": goal_prob
    }

    return jsonify({
        "metadata": {
            "num_simulations": num_simulations,
            "years": years
        },
        "summary": summary,
        "wealth_percentiles": wealth_percentiles
    })

if __name__ == '__main__':
    app.run(debug=True)
