 import pandas as pd

# Read the CSV file
df = pd.read_csv("departments.csv")

# Select distinct department IDs
distinct_dept_ids = df["DEPARTMENT_ID"].unique()

# Display the result
print("Distinct Department IDs:")
print(distinct_dept_ids)
