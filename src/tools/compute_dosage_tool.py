# compute_dosage_tool.py
# -------------------------------------------------------
# Tool Name  : A tool to compute safe medical dosages
# Domain     : Medical Logistics
# Author     : Sutton Wilterdink
# Description: This tool computes safe medical dosages 
#               of a given drug for which it is very 
#               important to be accurate to mitigate the 
#               chances of a patient overdose.
# Usage      : See README.md for a sample call.

def compute_dosage(weight_kg: float, drug_mg_per_kg: float, max_dose_mg: float) -> dict:
    """
    Computes the safe dosage of a drug in milligrams based on a patient's weight in kilograms

    Args:
        weight_kg (float): The patient's weight in kilograms
        drug_mg_per_kg (float): The drug's allowed dosage in milligrams per kilogram of patient body weight
        max_dose_mg (float): The maximum allowed dose of the drug

    Returns:
        dict: {
            "result" (float): The safe dosage of the drug in milligrams
            "unit" (str): "mg"
            "detail" (str): Verbose explanation of calculation
        }

    Raises:
        TypeError: if any input is outside of expected type
        ValueError: if any input is outside of expected range
    """
    # --- Input Validation ---
    # Type Checking
    if not isinstance(weight_kg, (int, float)):
        raise TypeError(f"Expected type int or float for weight_kg, got {type(weight_kg).__name__}")
    if not isinstance(drug_mg_per_kg, (int, float)):
        raise TypeError(f"Expected type int or float for drug_mg_per_kg, got {type(drug_mg_per_kg).__name__}")
    if not isinstance(max_dose_mg, (int, float)):
        raise TypeError(f"Expected type int or float for max_dose_mg, got {type(max_dose_mg).__name__}")
    # Range Checking
    if weight_kg <= 0:
        raise ValueError(f"Expected value > 0 for weight_kg, got {weight_kg}")
    if drug_mg_per_kg <= 0:
        raise ValueError(f"Expected value > 0 for drug_mg_per_kg, got {drug_mg_per_kg}")
    if max_dose_mg <= 0:
        raise ValueError(f"Expected value > 0 for max_dose_mg, got {max_dose_mg}")
    
    # --- Core Logic ---
    raw_dose = weight_kg * drug_mg_per_kg

    result = min(raw_dose, max_dose_mg)
    unit = "mg"
    detail = (
        f"The unbounded allowed dosage is {weight_kg:.4g} * {drug_mg_per_kg:.4g} "
        f"= {raw_dose:.4g}, which is "
        f"{'greater than' if raw_dose > max_dose_mg else 'less than'} "
        f"the maximum allowed dosage of {max_dose_mg:.4g}"
    )

    return {
        "result": result,
        "unit": unit,
        "detail": detail,
    }
