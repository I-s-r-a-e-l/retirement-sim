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
    print("Received JSON:", data)

    # --- Required fields and their default fallbacks ---
    required_fields = ['age', 'retirement_age', 'savings', 'return_rate', 'volatility',
                       'contribution', 'risk_tolerance', 'inflation_rate', 'wealth_goal']
    
    missing_fields = [field for field in required_fields if data.get(field) is None]
    if missing_fields:
        return jsonify({
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400

    # Extract inputs with fallback/defaults
    age = data['age']
    retirement_age = data['retirement_age']
    savings = data['savings']
    return_rate = data['return_rate']
    volatility = data['volatility']
    contribution = data['contribution']
    risk_tolerance = data['risk_tolerance']
    inflation_rate = data['inflation_rate']
    wealth_goal = data['wealth_goal']
    num_simulations = data.get('num_simulations', 10000)

    # Validate numeric ranges
    if retirement_age <= age:
        return jsonify({"error": "retirement_age must be greater than age"}), 400
    if not (0 <= return_rate <= 1) or not (0 <= volatility <= 1) or not (0 <= inflation_rate <= 1):
        return jsonify({"error": "return_rate, volatility, and inflation_rate must be between 0 and 1"}), 400

    # Adjust return/volatility based on risk
    if risk_tolerance == "conservative":
        return_rate -= 0.01
        volatility *= 0.75
    elif risk_tolerance == "aggressive":
        return_rate += 0.01
        volatility *= 1.25

    real_return_rate = return_rate - inflation_rate
    years = retirement_age - age
    all_simulations = []
    wealth_over_time = {f"year_{i}": [] for i in range(years + 1)}

    # --- Run Monte Carlo simulations ---
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

    # --- Percentiles per year ---
    final_values = [sim[-1] for sim in all_simulations]
    wealth_percentiles = {
        f"year_{i}": {
            "p10": round(np.percentile(wealth_over_time[f"year_{i}"], 10), 2),
            "p50": round(np.percentile(wealth_over_time[f"year_{i}"], 50), 2),
            "p90": round(np.percentile(wealth_over_time[f"year_{i}"], 90), 2)
        } for i in range(years + 1)
    }

    # --- Risk metrics ---
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
