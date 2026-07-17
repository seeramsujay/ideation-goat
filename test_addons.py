import os
import sys

# Force UTF-8 encoding on standard output for Windows consoles to support emojis/Unicode
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# Import the tools
from server import (
    verify_workspace_fit,
    compose_solution_stack,
    get_repo_health,
    profile_repo_hardware_footprint,
    align_system_architecture
)

async def run_tests():
    print("=== Testing verify_workspace_fit ===")
    try:
        res = await verify_workspace_fit("psf/requests", ".")
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

    print("\n=== Testing compose_solution_stack ===")
    try:
        res = await compose_solution_stack("secure backend and local database", n_results=1)
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

    print("\n=== Testing get_repo_health ===")
    try:
        res = await get_repo_health("psf/requests")
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

    print("\n=== Testing profile_repo_hardware_footprint ===")
    try:
        res = await profile_repo_hardware_footprint("lvgl/lvgl", "ESP32")
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

    print("\n=== Testing align_system_architecture ===")
    try:
        res = await align_system_architecture("SQLAlchemy", ".")
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_tests())
