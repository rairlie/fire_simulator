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
portfolios = config["portfolios"]

# Work out years
reduced_spending_year = reduced_spending_age - start_age
pension_start_year = pension_start_age - start_age
inheritance_year = inheritance_age - start_age
n_years = end_age - start_age

# Storage for results
ending_capitals = [[] for _ in range(len(portfolios))]

np.random.seed(1)

for index, portfolio in enumerate(portfolios):
    real_return = portfolio["real_return"]
    std = portfolio["std"]

    for _ in range(n_simulations):
        capital = initial_capital

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
                capital += inheritance_amount

            # Simulate returns and withdraw
            ret = np.random.normal(real_return, std)

            capital = max(0, capital * (1 + ret) - withdrawal)

        ending_capitals[index].append(capital)


# Summarize Results
frames = {}
summary = {
    'Metric': ['Mean', 'Median', '10th Percentile', '15th Percentile', '20th Percentile', '25th Percentile', '75th Percentile', '90th Percentile', 'Failure Rate (Capital=0)'],
}
for index, portfolio in enumerate(portfolios):
    p_ending_capitals = ending_capitals[index]

    frames[portfolio["name"]] = p_ending_capitals
    summary[portfolio["name"]] = [
        np.mean(p_ending_capitals),
        np.median(p_ending_capitals),
        np.percentile(p_ending_capitals, 10),
        np.percentile(p_ending_capitals, 15),
        np.percentile(p_ending_capitals, 20),
        np.percentile(p_ending_capitals, 25),
        np.percentile(p_ending_capitals, 75),
        np.percentile(p_ending_capitals, 90),
        np.sum(np.array(p_ending_capitals) == 0) / n_simulations
    ]

df = pd.DataFrame(frames)
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
    worksheet.set_column(1, len(portfolios), 20, format1)

print("Simulation complete. Results saved to '" + output_file + "'")
