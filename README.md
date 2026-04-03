# Retirement Portfolio Simulator

A Monte Carlo retirement model that projects how your savings can grow over time. It uses random market scenarios to estimate outcomes, risk levels, and the chance you hit your goal.

## What It Does

- Simulates retirement savings with 10,000+ scenarios
- Handles stocks/bonds/cash allocation
- Includes annual contributions and retirement withdrawals
- Gives stats: median outcome, 10th/90th percentiles, VaR, survival chance

## Quick Start

1. Install dependencies:
```bash
pip install flask==3.0.3 numpy==1.24.3
```
2. Run the app:
```bash
python app.py
```
3. Open request tool (curl or Postman) and send to `http://127.0.0.1:5000/simulate`

## Simple Example

```bash
curl -X POST http://127.0.0.1:5000/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "age": 20,
    "retirement_age": 65,
    "savings": 5000,
    "contribution": 3000
  }'
```

### Key output fields
- `median`: typical final savings
- `percentile_10`: conservative end result
- `percentile_90`: strong outcome
- `probability_reaching_goal`: chance to meet target
- `survival_probability`: chance money lasts through retirement

## Optional Advanced Configuration

You can include extra fields in request JSON:
- `stock_allocation`, `bond_allocation`, `cash_allocation`
- `contribution_growth_rate`, `withdrawal_rate`
- `n_simulations` (bigger makes it more accurate)

## Note

This is a learning tool, not investment advice. Real investing should include professional guidance.

---

Advanced users: full API and advanced modeling details are in the code comments and in more detailed sections of this file.
    "percentile_90": 3200000,
    "var_5": 450000,
    "probability_reaching_goal": 0.87,
    "survival_probability": 0.92,
    "average_max_drawdown": 0.28
  }
}
```

### Python Example

```python
import requests

# Your retirement plan
data = {
    "age": 20,
    "retirement_age": 65,
    "savings": 5000,
    "contribution": 3000,
    "stock_allocation": 0.8,  # 80% stocks (aggressive)
    "bond_allocation": 0.2    # 20% bonds
}

response = requests.post("http://127.0.0.1:5000/simulate", json=data)
result = response.json()

print(f"Median savings at retirement: ${result['summary']['median']:,.0f}")
print(f"Chance of reaching $1M: {result['summary']['probability_reaching_goal']*100:.0f}%")
```

## API Parameters

### Required
- `age` - Your current age
- `retirement_age` - When you want to retire
- `savings` - Money you have saved now
- `contribution` - How much you save per year

### Optional (Advanced)
- `stock_allocation` - % in stocks (0.0 to 1.0) [default: 0.6]
- `bond_allocation` - % in bonds [default: 0.3]
- `cash_allocation` - % in cash [default: 0.1]
- `contribution_growth_rate` - Annual salary increase [default: 0.03]
- `withdrawal_rate` - % withdrawn in retirement [default: 0.04]
- `n_simulations` - Number of scenarios to test [default: 10,000]

## What Makes This Cool

### 🧮 **Monte Carlo Simulation**
Instead of guessing "you'll have X dollars," it runs thousands of "what if" scenarios with different market conditions, giving you a probability distribution of outcomes.

### 📊 **Real Market Math**
- **Lognormal returns**: Markets grow multiplicatively (not additively), so we use lognormal distributions that match real stock behavior
- **Correlations**: Stocks and bonds don't move independently - we model their relationships
- **Inflation**: Everything adjusts for rising prices over time

### 🎯 **Advanced Risk Analysis**
- **VaR (Value at Risk)**: "In the worst 5% of scenarios, you might have this much" - industry-standard risk metric
- **Survival Probability**: Chance your money lasts through retirement
- **Max Drawdown**: Biggest drop you'd experience

### 🔄 **Dynamic Planning**
- Contributions grow with your salary increases
- Withdrawals in retirement follow the proven "4% rule"
- Multi-asset portfolios with realistic return assumptions
- Full retirement phase simulation (not just saving)

### ⚡ **Performance & Scale**
- **10,000+ simulations** per request for statistical accuracy
- **Fast NumPy computations** handle complex calculations quickly
- **Production-ready API** with proper error handling and validation

## Understanding Results

| Metric | What It Means |
|--------|---------------|
| `median` | Middle scenario - 50% chance you'll do better, 50% worse |
| `percentile_10` | Bad scenario - only 10% chance of doing worse |
| `percentile_90` | Great scenario - only 10% chance of doing better |
| `probability_reaching_goal` | % chance you hit your retirement target |
| `survival_probability` | % chance your money lasts 30+ years in retirement |

## Project Structure

```
retirement-sim/
├── app.py              # Main Flask app with simulation logic
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .gitignore         # Files to ignore in git
```

## Technical Details

### Asset Assumptions (Based on Historical Data)
- **Stocks**: 8% average annual return, 15% volatility (S&P 500 historical averages)
- **Bonds**: 4% average annual return, 8% volatility (US Treasury bonds)
- **Cash**: 2% average annual return, 1% volatility (money market funds)
- **Correlation**: Stocks/bonds correlation coefficient of 0.3 (realistic diversification)

### Simulation Engine
- **NumPy arrays**: Vectorized operations for performance
- **Multivariate normal sampling**: Correlated returns using Cholesky decomposition
- **Geometric returns**: `wealth *= exp(log_return)` for multiplicative growth
- **Stochastic inflation**: Independent normal distribution sampling
- **Memory efficient**: No Python loops in hot path, pure NumPy operations

### API Architecture
- **Flask REST API**: Clean endpoints with JSON request/response
- **Input validation**: Type checking, bounds validation, allocation constraints
- **Error handling**: Proper HTTP status codes (400, 500) with descriptive messages
- **Logging**: Structured logging for debugging and monitoring
- **Health checks**: `/health` endpoint for deployment monitoring

### Mathematical Models

**Lognormal Returns Formula:**
```
log_return = Normal(μ - σ²/2, σ)  # Drift-adjusted for lognormal
wealth = wealth * exp(log_return)  # Multiplicative growth
```

**Multivariate Correlations:**
```
Σ = covariance_matrix  # From volatilities and correlations
returns = multivariate_normal(means, Σ)  # Correlated sampling
```

**Risk Metrics:**
```
VaR_5 = percentile(wealths, 5)  # 5th percentile
CVaR_5 = mean(wealths[wealths ≤ VaR_5])  # Conditional tail expectation
Survival = mean(wealths > 0)  # Probability of positive wealth
```

## Important Notes

⚠️ **This is for learning/planning only** - Not financial advice!
- Assumes historical market patterns continue
- Doesn't include taxes, fees, or market crashes
- Real retirement planning needs professional help

## Future Ideas

- Web interface (React/Vue)
- More asset classes (real estate, crypto)
- Tax calculations
- Mobile app
- Historical market data integration

---

Built by Israel Adeboga - Exploring Python, finance, and probabilistic modeling!
