import pandas as pd

student_data = pd.DataFrame(columns=["Student", "Grade"])



def calculate_stats(df):
    average_grade = df["Grade"].mean(axis=0)
    return average_grade

print(calculate_stats(student_data))