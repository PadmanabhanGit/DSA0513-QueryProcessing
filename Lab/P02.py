import pandas as pd

# Read the CSV file
df = pd.read_csv("job_history.csv")

# Count the number of jobs for each employee
job_count = df.groupby('EMPLOYEE_ID').size()

# Select employees with two or more jobs
employees = job_count[job_count >= 2].index

# Display the employee IDs
print("Employees who have done two or more jobs in the past:")
print(list(employees))
