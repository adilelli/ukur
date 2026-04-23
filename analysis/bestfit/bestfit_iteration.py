import numpy as np
import pandas as pd

def fit_model(x, y, terms):
    """Fit linear model and return coefficients, predictions, and residuals."""
    # Basis functions
    basis = {
        'x2':    lambda x: x**2,
        'x':     lambda x: x,
        'xlogx': lambda x: x * np.log(x),
        'logx':  lambda x: np.log(x),
        'const': lambda x: np.ones_like(x)
    }
    
    X = np.column_stack([basis[t](x) for t in terms])
    coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    y_pred = X @ coeffs
    residuals = y - y_pred
    return coeffs, y_pred, residuals

def model_metrics(x, y, terms):
    """Compute R², adjusted R², AIC, BIC, RMSE for a given set of terms."""
    n = len(y)
    k = len(terms)          # number of predictors (including constant if present)
    
    coeffs, y_pred, residuals = fit_model(x, y, terms)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r2 = 1 - ss_res / ss_tot
    r2_adj = 1 - (1 - r2) * (n - 1) / (n - k - 1)   # if constant is included
    # If constant is not in terms, adjust formula; but here constant is always last.
    
    # For AIC/BIC, we use Gaussian likelihood: AIC = n * ln(SSR/n) + 2k + constant
    # Typically, we compare relative AIC/BIC, so constant can be dropped.
    sigma2 = ss_res / n
    aic = n * np.log(sigma2) + 2 * k
    bic = n * np.log(sigma2) + k * np.log(n)
    rmse = np.sqrt(ss_res / n)
    
    return {
        'k': k,
        'R²': r2,
        'Adj R²': r2_adj,
        'AIC': aic,
        'BIC': bic,
        'RMSE': rmse
    }

# Example data
x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
y = np.array([2.5, 3.7, 4.2, 5.1, 6.3, 7.8, 9.0, 10.5, 12.1, 14.0])

# Define term sets for the five models
term_sets = [
    ['x2', 'x', 'xlogx', 'logx', 'const'],   # full
    ['x', 'xlogx', 'logx', 'const'],          # drop a
    ['xlogx', 'logx', 'const'],               # drop a,b
    ['x', 'const'],                        # drop a,b,c
    ['const']                                 # only e
]

# Compute metrics for each model
results = []
for i, terms in enumerate(term_sets, start=1):
    metrics = model_metrics(x, y, terms)
    results.append({
        'Model': f'Model {i}: {terms}',
        **metrics
    })

# Display comparison table
df = pd.DataFrame(results)
print(df.to_string(float_format="%.4f"))