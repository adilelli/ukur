import numpy as np

def fit_model(x, y, terms):
    """
    Fit a linear model y = sum_{t in terms} coefficient[t] * basis_t(x)
    
    Parameters:
        x (array): x data (must be >0 if log terms used)
        y (array): y data
        terms (list): list of strings indicating which basis functions to include.
                      Supported: 'x2', 'x', 'xlogx', 'logx', 'const'
    
    Returns:
        dict: coefficients for each term
        array: predicted y values
    """
    # Map term names to functions that compute the column for given x
    basis_functions = {
        'x2':    lambda x: x**2,
        'x':     lambda x: x,
        'xlogx': lambda x: x * np.log(x),
        'logx':  lambda x: np.log(x),
        'const': lambda x: np.ones_like(x)
    }
    
    # Build design matrix X
    X = np.column_stack([basis_functions[term](x) for term in terms])
    print(x)
    
    # Solve least squares
    coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    
    # Predict
    y_pred = X @ coeffs
    
    # Return coefficients as dictionary
    coef_dict = {term: coeffs[i] for i, term in enumerate(terms)}
    return coef_dict, y_pred

# Example data (replace with your actual data)
x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])  # must be >0
y = np.array([2.5, 3.7, 4.2, 5.1, 6.3, 7.8, 9.0, 10.5, 12.1, 14.0])

# Define the term sets for the five models
term_sets = [
    ['x2', 'x', 'xlogx', 'logx', 'const'],   # full
    ['x', 'xlogx', 'logx', 'const'],          # drop a
    ['x', 'logx', 'const'],               # drop a,b
    ['x', 'const'],                        # drop a,b,c
    # ['const']                                 # only e
]

# Fit each model and print coefficients
for i, terms in enumerate(term_sets, start=1):
    coeffs, y_pred = fit_model(x, y, terms)
    print(f"Model {i}: terms = {terms}")
    for term, coef in coeffs.items():
        print(f"  {term}: {coef:.6f}")
    print()