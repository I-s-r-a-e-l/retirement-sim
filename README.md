# Retirement Portfolio Simulator

A sophisticated Monte Carlo simulation tool for retirement planning, built with Flask and NumPy. Uses realistic financial modeling with lognormal returns, multi-asset allocation, and dynamic contribution growth.

## Features

- **Advanced Monte Carlo Method**: 10,000+ simulations per request
- **Lognormal Returns**: Realistic multiplicative market growth modeling
- **Multi-Asset Portfolio**: Stocks, bonds, and cash with configurable correlations
- **Dynamic Contributions**: Annual salary growth during accumulation phase
- **Retirement Phase**: Configurable withdrawal strategies (4% rule by default)
- **Risk Metrics**: VaR, CVaR, max drawdown, survival probability
- **Production-Ready**: Input validation, error handling, health checks, logging

## Installation

### Prerequisites
- Python 3.9+
- pip or conda

### Setup

1. **Clone and navigate to the project:**
```bash
cd retirement-sim
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

### Running the Server (Development)

```bash
FLASK_ENV=development python app.py
```

Server runs on `http://127.0.0.1:5000`

### Running the Server (Production)

```bash
FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## API Endpoints

### POST /simulate

**Description**: Run a Monte Carlo retirement portfolio simulation

**Request Body (JSON):**

```json
{
  "age": 30,
  "retirement_age": 65,
  "savings": 100000,
  "contribution": 10000,
  "goal": 1000000,
  "n_simulations": 10000,
  "inflation_rate": 0.03,
  "inflation_vol": 0.02,
  "stock_allocation": 0.6,
  "bond_allocation": 0.3,
  "cash_allocation": 0.1,
  "stock_return": 0.08,
  "stock_vol": 0.15,
  "bond_return": 0.04,
  "bond_vol": 0.08,
  "cash_return": 0.02,
  "cash_vol": 0.01,
  "correlation_stock_bond": 0.3,
  "contribution_growth_rate": 0.03,
  "withdrawal_rate": 0.04,
  "retirement_duration": 30
}
```

**Required Fields:**
- `age` (int): Current age, 18-120
- `retirement_age` (int): Target retirement age
- `savings` (float): Current savings in dollars, 0-100M
- `contribution` (float): Annual contribution in dollars, 0-1M

**Optional Fields (defaults shown):**
- `goal` (float): Retirement savings target [default: 1,000,000]
- `n_simulations` (int): Number of simulations [default: 10,000]
- `inflation_rate` (float): Expected inflation [default: 0.03]
- `inflation_vol` (float): Inflation volatility [default: 0.02]
- `stock_allocation` (float): Fraction in stocks [default: 0.6]
- `bond_allocation` (float): Fraction in bonds [default: 0.3]
- `cash_allocation` (float): Fraction in cash [default: 0.1]
- `stock_return` (float): Expected stock return [default: 0.08]
- `stock_vol` (float): Stock volatility [default: 0.15]
- `bond_return` (float): Expected bond return [default: 0.04]
- `bond_vol` (float): Bond volatility [default: 0.08]
- `cash_return` (float): Expected cash return [default: 0.02]
- `cash_vol` (float): Cash volatility [default: 0.01]
- `correlation_stock_bond` (float): Stock-bond correlation [default: 0.3]
- `contribution_growth_rate` (float): Annual contribution growth [default: 0.03]
- `withdrawal_rate` (float): Annual withdrawal rate in retirement [default: 0.04]
- `retirement_duration` (int): Years to simulate post-retirement [default: 30]

**Response (200 OK):**

```json
{
  "summary": {
    "median": 2500000,
    "percentile_10": 1200000,
    "percentile_90": 4500000,
    "var_5": 800000,
    "cvar_5": 650000,
    "probability_reaching_goal": 0.92,
    "survival_probability": 0.88,
    "average_max_drawdown": 0.35,
    "volatility": 750000
  }
}
```

**Response Fields:**
- `median`: Median final wealth at end of retirement
- `percentile_10` / `percentile_90`: 10th and 90th percentile outcomes
- `var_5`: Value at Risk (5th percentile, worst 5% of scenarios)
- `cvar_5`: Conditional VaR (average loss in worst 5% of scenarios)
- `probability_reaching_goal`: Percentage of simulations reaching target goal
- `survival_probability`: Percentage of simulations with positive wealth post-retirement
- `average_max_drawdown`: Average maximum drawdown across all simulations
- `volatility`: Standard deviation of final wealth outcomes

**Error Responses:**

```json
// 400 Bad Request - Invalid parameters
{
  "error": "Age must be between 18 and 120"
}

// 500 Internal Server Error
{
  "error": "Internal server error"
}
```

### GET /health

**Description**: Health check endpoint for monitoring and load balancers

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "retirement-simulator"
}
```

## Example Usage

### Using cURL

```bash
curl -X POST http://127.0.0.1:5000/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "retirement_age": 65,
    "savings": 250000,
    "contribution": 15000,
    "stock_allocation": 0.7,
    "bond_allocation": 0.2,
    "cash_allocation": 0.1
  }'
```

### Using Python

```python
import requests
import json

url = "http://127.0.0.1:5000/simulate"
payload = {
    "age": 35,
    "retirement_age": 65,
    "savings": 250000,
    "contribution": 15000,
    "n_simulations": 5000
}

response = requests.post(url, json=payload)
result = response.json()
print(f"Median portfolio at retirement: ${result['summary']['median']:,.0f}")
print(f"Success probability: {result['summary']['probability_reaching_goal']*100:.1f}%")
```

### Using JavaScript/Node.js

```javascript
const payload = {
  age: 35,
  retirement_age: 65,
  savings: 250000,
  contribution: 15000
};

fetch('http://127.0.0.1:5000/simulate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
})
  .then(r => r.json())
  .then(data => {
    console.log(`Median: $${data.summary.median.toLocaleString()}`);
    console.log(`Success rate: ${(data.summary.probability_reaching_goal * 100).toFixed(1)}%`);
  });
```

## Configuration

Set environment variables to customize behavior:

```bash
export FLASK_ENV=production          # development or production
export HOST=0.0.0.0                  # Bind address
export PORT=8000                     # Server port
```

## Model Assumptions

### Asset Returns
- **Stocks**: 8% annual return, 15% volatility
- **Bonds**: 4% annual return, 8% volatility
- **Cash**: 2% annual return, 1% volatility
- **Correlation**: Stocks and bonds: 0.3, cash uncorrelated

### Distribution
- Returns follow a **lognormal distribution** (geometric Brownian motion)
- Inflation is independently sampled with normal distribution

### Contribution & Withdrawal
- Contributions grow at 3% annually (matching salary growth)
- Retirement withdrawals use 4% rule (1/life expectancy at retirement)

## Limitations & Important Notes

This is a **probabilistic planning tool**, not a forecast:
- Assumes historical return distributions continue
- Ignores taxes, fees, and market regime changes
- Uses simplified 3-asset model (real portfolios are more complex)
- Does not account for lifestyle changes or emergency spending
- Assumes rebalancing and no behavioral bias

**For important financial decisions, consult a professional advisor.**

## Deployment

### Docker

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
ENV FLASK_ENV=production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

### Heroku

```bash
git push heroku main
```

### AWS/Azure/GCP

Deploy with gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Development

### Running Tests

```bash
# (Add pytest-based tests in future)
python -m pytest tests/
```

### Code Style

```bash
pip install black flake8
black app.py
flake8 app.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'flask'` | Run `pip install -r requirements.txt` |
| Port 5000 already in use | Change port: `PORT=8001 python app.py` |
| `debug=True` warnings in production | Set `FLASK_ENV=production` |
| Out of memory with large n_simulations | Reduce to 5000 or run on larger instance |

## License

MIT License - Feel free to use and modify.

## Changelog

- **v2.0** (Apr 2026): Enhanced Monte Carlo with lognormal returns, multi-asset allocation, dynamic contributions, retirement phase modeling
- **v1.0** (Jun 2025): Original simple normal-distribution simulator

## Contributing

Pull requests welcome. Please:
1. Add tests for new features
2. Update README with usage examples
3. Follow PEP 8 style guide
