import numpy as np
import pandas as pd
import json

with open('config.json') as f:
    config = json.load(f)

# Assign Parameters
n_simulations = config["n_simulations"]
initial_capital = config["initial_capital"]

start_age = config["start_age"]
end_age = config["end_age"]
reduced_spending_age = config["reduced_spending_age"]

full_withdrawal = config["full_withdrawal"]
reduced_withdrawal = config["reduced_withdrawal"]

inheritance_age = config["inheritance_age"]
inheritance_amount = config["inheritance_amount"]

pension_start_age = config["pension_start_age"]
state_pension_income = config["state_pension_income"]

# Portfolio Return Assumptions (real, net of inflation)
vwrp_mean = config["vwrp_mean"]
vwrp_std = config["vwrp_std"]
sixty40_mean = config["sixty40_mean"]
sixty40_std = config["sixty40_std"]

# Work out years
reduced_spending_year = reduced_spending_age - start_age
pension_start_year = pension_start_age - start_age
inheritance_year = inheritance_age - start_age
n_years = end_age - start_age

# Storage for results
vwrp_ending_capitals = []
sixty40_ending_capitals = []

np.random.seed(42)

for _ in range(n_simulations):
    capital_vwrp = initial_capital
    capital_6040 = initial_capital

    for year in range(n_years):
        # Determine current withdrawal need
        if year >= reduced_spending_year:
            withdrawal = reduced_withdrawal
        else:
            withdrawal = full_withdrawal

        # Subtract pension income if applicable
        if year >= pension_start_year:
            withdrawal = max(0, withdrawal - state_pension_income)

        # Apply inheritance
        if year == inheritance_year:
            capital_vwrp += inheritance_amount
            capital_6040 += inheritance_amount

        # Simulate returns and withdraw
        r_vwrp = np.random.normal(vwrp_mean, vwrp_std)
        r_6040 = np.random.normal(sixty40_mean, sixty40_std)

        capital_vwrp = max(0, capital_vwrp * (1 + r_vwrp) - withdrawal)
        capital_6040 = max(0, capital_6040 * (1 + r_6040) - withdrawal)

    vwrp_ending_capitals.append(capital_vwrp)
    sixty40_ending_capitals.append(capital_6040)

# Summarize Results
df = pd.DataFrame({
    'VWRP Ending Capital (£)': vwrp_ending_capitals,
    '60/40 Ending Capital (£)': sixty40_ending_capitals
})

summary = {
    'Metric': ['Mean', 'Median', '10th Percentile', '25th Percentile', '75th Percentile', '90th Percentile', 'Failure Rate (Capital=0)'],
    'VWRP': [
        np.mean(vwrp_ending_capitals),
        np.median(vwrp_ending_capitals),
        np.percentile(vwrp_ending_capitals, 10),
        np.percentile(vwrp_ending_capitals, 25),
        np.percentile(vwrp_ending_capitals, 75),
        np.percentile(vwrp_ending_capitals, 90),
        np.sum(np.array(vwrp_ending_capitals) == 0) / n_simulations
    ],
    '60/40': [
        np.mean(sixty40_ending_capitals),
        np.median(sixty40_ending_capitals),
        np.percentile(sixty40_ending_capitals, 10),
        np.percentile(sixty40_ending_capitals, 25),
        np.percentile(sixty40_ending_capitals, 75),
        np.percentile(sixty40_ending_capitals, 90),
        np.sum(np.array(sixty40_ending_capitals) == 0) / n_simulations
    ]
}

df_summary = pd.DataFrame(summary)

# Export to Excel
output_file = 'fire_simulation.xlsx'

with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    df_summary.to_excel(writer, sheet_name='Summary Statistics', index=False)
    df.to_excel(writer, sheet_name='Simulation Data', index=False)

    workbook = writer.book
    worksheet = writer.sheets["Summary Statistics"]
    format1 = workbook.add_format({"num_format": "#,##0.00"})
    worksheet.set_column(0, 0, 20, None)
    worksheet.set_column(1, 2, 20, format1)

print("Simulation complete. Results saved to '" + output_file + "'")
