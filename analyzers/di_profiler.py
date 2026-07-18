import os
import re
from typing import Dict, Any, List

def profile_workspace_di(workspace_path: str) -> Dict[str, Any]:
    """
    Scans a workspace directory to detect class structures, constructor parameters,
    and decorator patterns to score dependency injection patterns and coupling.
    """
    workspace = os.path.abspath(workspace_path)
    report = {
        "workspace_path": workspace,
        "scanned_files": 0,
        "classes_detected": 0,
        "di_classes_count": 0,
        "tightly_coupled_instantiations": 0,
        "di_score": 100.0,
        "di_grade": "A",
        "details": [],
        "recommendations": []
    }
    
    # Regex pattern searches
    # TypeScript/JavaScript constructor injection: constructor(private db: DB)
    ts_di_pattern = re.compile(r"constructor\s*\(\s*(?:private|public|protected|readonly)?\s*\w+\s*:\s*\w+")
    # TS/JS decorators: @inject(), @injectable(), @singleton()
    decorator_pattern = re.compile(r"@(?:inject|injectable|singleton|service|provide)\b")
    # Python constructor injection: def __init__(self, db: Database) or dependency-injection package syntax
    py_di_pattern = re.compile(r"def\s+__init__\s*\(\s*self\s*,\s*\w+\s*:\s*\w+")
    # Python direct coupling anti-pattern: x = Database() inside class body/methods
    py_tight_coupling = re.compile(r"\bself\.\w+\s*=\s*(?:[A-Z]\w+)\(\)")
    
    for root, _, files in os.walk(workspace):
        # Skip hidden directories and virtual envs
        if any(part.startswith('.') or part in ['node_modules', 'venv', '.venv', '__pycache__'] for part in root.split(os.sep)):
            continue
            
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in ['.py', '.ts', '.tsx', '.js', '.jsx', '.java']:
                continue
                
            report["scanned_files"] += 1
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                lines = content.splitlines()
                has_class = False
                di_class_signals = 0
                coupled_signals = 0
                
                # Check line by line for architectural features
                for idx, line in enumerate(lines):
                    # Check for class declarations
                    if "class " in line:
                        report["classes_detected"] += 1
                        has_class = True
                        
                    # Check for DI patterns
                    if decorator_pattern.search(line):
                        di_class_signals += 1
                    if py_di_pattern.search(line) or ts_di_pattern.search(line):
                        di_class_signals += 1
                        
                    # Check for tightly coupled instantiations (Anti-pattern: instantiating service inside constructor/method)
                    if py_tight_coupling.search(line) or ("new " in line and "class " not in line and "constructor" not in line and "=" in line):
                        coupled_signals += 1
                        report["tightly_coupled_instantiations"] += 1
                        
                if has_class:
                    rel_path = os.path.relpath(file_path, workspace)
                    if di_class_signals > 0:
                        report["di_classes_count"] += 1
                        
                    report["details"].append({
                        "file": rel_path,
                        "di_indicators": di_class_signals,
                        "coupled_indicators": coupled_signals,
                        "score": max(0.0, 100.0 - (coupled_signals * 20.0))
                    })
                    
            except Exception:
                pass

    # Calculate DI Score
    # Score penalty: -15 per coupled instantiation, bonus if DI is utilized across classes
    total_classes = report["classes_detected"]
    if total_classes > 0:
        di_ratio = report["di_classes_count"] / total_classes
        # base score incorporates proportion of classes using DI
        report["di_score"] = 60.0 + (di_ratio * 40.0)
        # deduct for tightly coupled codes
        report["di_score"] -= (report["tightly_coupled_instantiations"] * 10.0)
    else:
        report["di_score"] = 100.0
        
    report["di_score"] = max(0.0, min(100.0, report["di_score"]))
    
    # Assign Grade
    score = report["di_score"]
    if score >= 90.0:
        report["di_grade"] = "A"
    elif score >= 80.0:
        report["di_grade"] = "B"
    elif score >= 70.0:
        report["di_grade"] = "C"
    elif score >= 60.0:
        report["di_grade"] = "D"
    else:
        report["di_grade"] = "F"
        
    # Generate recommendations
    if report["tightly_coupled_instantiations"] > 0:
        report["recommendations"].append(
            f"Decouple direct class constructions. Instead of instantiating helper/adapter modules internally, "
            f"inject them through constructor parameters to permit unit testing mock boundaries."
        )
    if total_classes > 0 and report["di_classes_count"] == 0:
        report["recommendations"].append(
            "Adopt standard Dependency Injection containers or factory pattern modules to manage service lifecycles."
        )
    if not report["recommendations"]:
        report["recommendations"].append("Workspace conforms to high-quality decoupled DI architecture models.")
        
    return report
