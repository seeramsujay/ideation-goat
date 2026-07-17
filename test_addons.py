import os
import sys

# Import the tools
from mcp_server import (
    verify_workspace_fit,
    compose_solution_stack,
    get_repo_health,
    profile_repo_hardware_footprint,
    align_system_architecture
)

def run_tests():
    print("=== Testing verify_workspace_fit ===")
    try:
        res = verify_workspace_fit("psf/requests", ".")
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

    print("\n=== Testing compose_solution_stack ===")
    try:
        res = compose_solution_stack("secure backend and local database", n_results=1)
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

    print("\n=== Testing get_repo_health ===")
    try:
        res = get_repo_health("psf/requests")
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

    print("\n=== Testing profile_repo_hardware_footprint ===")
    try:
        res = profile_repo_hardware_footprint("lvgl/lvgl", "ESP32")
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

    print("\n=== Testing align_system_architecture ===")
    try:
        res = align_system_architecture("SQLAlchemy", ".")
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

if __name__ == "__main__":
    run_tests()
