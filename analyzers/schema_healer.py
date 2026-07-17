import json
from typing import Dict, Any, Tuple

def heal_parameter_schema(raw_args: Dict[str, Any], expected_schema: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Validates, coerces, and corrects raw parameters against an expected schema map.
    
    expected_schema structure:
    {
        "field_name": {
            "type": int/float/str/bool/list/dict,
            "default": default_value,
            "required": True/False,
            "choices": ["option1", "option2"]
        }
    }
    
    Returns:
        healed_params (dict): The corrected parameters.
        audit_log (dict): Explanations of changes made.
    """
    healed_params = {}
    audit_log = {}
    
    for field, rules in expected_schema.items():
        field_type = rules.get("type")
        default_val = rules.get("default")
        choices = rules.get("choices")
        required = rules.get("required", False)
        
        # Check if field exists
        if field not in raw_args:
            if required:
                healed_params[field] = default_val
                audit_log[field] = f"Missing required parameter. Applied default: '{default_val}'."
            else:
                if default_val is not None:
                    healed_params[field] = default_val
                    audit_log[field] = f"Applied optional default: '{default_val}'."
            continue
            
        val = raw_args[field]
        
        # Type Coercion Logic
        if field_type == int:
            try:
                healed_params[field] = int(val)
                if not isinstance(val, int):
                    audit_log[field] = f"Coerced '{val}' ({type(val).__name__}) to integer."
            except (ValueError, TypeError):
                healed_params[field] = default_val if default_val is not None else 0
                audit_log[field] = f"Failed to coerce '{val}' to integer. Replaced with fallback '{healed_params[field]}'."
                
        elif field_type == float:
            try:
                healed_params[field] = float(val)
                if not isinstance(val, float) and not isinstance(val, int):
                    audit_log[field] = f"Coerced '{val}' ({type(val).__name__}) to float."
            except (ValueError, TypeError):
                healed_params[field] = default_val if default_val is not None else 0.0
                audit_log[field] = f"Failed to coerce '{val}' to float. Replaced with fallback '{healed_params[field]}'."
                
        elif field_type == bool:
            if isinstance(val, str):
                val_clean = val.lower().strip()
                if val_clean in ["true", "1", "yes", "on", "t"]:
                    healed_params[field] = True
                    audit_log[field] = f"Coerced string '{val}' to True."
                elif val_clean in ["false", "0", "no", "off", "f"]:
                    healed_params[field] = False
                    audit_log[field] = f"Coerced string '{val}' to False."
                else:
                    healed_params[field] = default_val if default_val is not None else False
                    audit_log[field] = f"Ambiguous boolean string '{val}'. Set to default '{healed_params[field]}'."
            else:
                healed_params[field] = bool(val)
                if not isinstance(val, bool):
                    audit_log[field] = f"Coerced '{val}' to boolean."
                    
        elif field_type == str:
            healed_params[field] = str(val)
            # Enum Choice Typo Correction
            if choices:
                val_str = str(val).strip().lower()
                choices_lower = [c.lower() for c in choices]
                
                if val_str in choices_lower:
                    # Match exact casing from choices list
                    idx = choices_lower.index(val_str)
                    healed_params[field] = choices[idx]
                else:
                    # Typo search (fuzzy match / substring match)
                    matched_choice = None
                    for c in choices:
                        c_lower = c.lower()
                        # Checks if either is a substring of the other or character distance is close
                        if c_lower in val_str or val_str in c_lower:
                            matched_choice = c
                            break
                    if matched_choice:
                        healed_params[field] = matched_choice
                        audit_log[field] = f"Corrected typo/value '{val}' to match choices option '{matched_choice}'."
                    else:
                        healed_params[field] = default_val if default_val is not None else choices[0]
                        audit_log[field] = f"Invalid option '{val}' not in choices. Reset to fallback '{healed_params[field]}'."
                        
        elif field_type == list:
            if isinstance(val, str):
                # Try parsing as JSON list
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, list):
                        healed_params[field] = parsed
                        audit_log[field] = "Parsed JSON string into list."
                    else:
                        healed_params[field] = [val]
                        audit_log[field] = "Encapsulated string value into list container."
                except Exception:
                    # Comma separated fallback
                    healed_params[field] = [item.strip() for item in val.split(",") if item.strip()]
                    audit_log[field] = "Split comma-separated string value into list."
            elif isinstance(val, list):
                healed_params[field] = val
            else:
                healed_params[field] = [val]
                audit_log[field] = "Encapsulated value into list container."
                
        elif field_type == dict:
            if isinstance(val, str):
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, dict):
                        healed_params[field] = parsed
                        audit_log[field] = "Parsed JSON string into dict."
                    else:
                        healed_params[field] = {}
                        audit_log[field] = "Failed to convert string to dict. Replaced with empty dict."
                except Exception:
                    healed_params[field] = {}
                    audit_log[field] = "Failed to parse JSON string. Replaced with empty dict."
            elif isinstance(val, dict):
                healed_params[field] = val
            else:
                healed_params[field] = {}
                audit_log[field] = f"Cannot coerce type {type(val).__name__} to dict. Replaced with empty dict."
        else:
            healed_params[field] = val
            
    return healed_params, audit_log
