import pandas as pd


def calculate_stats(df):
    """
    Calculate statistical metrics for student grades.
    
    Args:
        df: DataFrame with columns ['Name', 'Grade']
    
    Returns:
        dict: Contains mean, median, min, max, std dev of grades
    """
    if df.empty or 'Grade' not in df.columns:
        return {
            'mean': 0,
            'median': 0,
            'min': 0,
            'max': 0,
            'std': 0,
            'count': 0
        }
    
    grades = df['Grade'].astype(float)
    
    return {
        'mean': round(grades.mean(), 2),
        'median': round(grades.median(), 2),
        'min': int(grades.min()),
        'max': int(grades.max()),
        'std': round(grades.std(), 2),
        'count': len(grades)
    }


def get_grade_distribution(df):
    """
    Create a grade distribution grouped by brackets (0-59, 60-69, etc).
    
    Args:
        df: DataFrame with columns ['Name', 'Grade']
    
    Returns:
        pd.DataFrame: Grade brackets and their counts
    """
    if df.empty or 'Grade' not in df.columns:
        return pd.DataFrame({
            'Grade Bracket': ['0-59', '60-69', '70-79', '80-89', '90-100'],
            'Count': [0, 0, 0, 0, 0]
        })
    
    grades = df['Grade'].astype(float)
    
    brackets = {
        '0-59': len(grades[(grades >= 0) & (grades < 60)]),
        '60-69': len(grades[(grades >= 60) & (grades < 70)]),
        '70-79': len(grades[(grades >= 70) & (grades < 80)]),
        '80-89': len(grades[(grades >= 80) & (grades < 90)]),
        '90-100': len(grades[(grades >= 90) & (grades <= 100)])
    }
    
    return pd.DataFrame({
        'Grade Bracket': list(brackets.keys()),
        'Count': list(brackets.values())
    })
