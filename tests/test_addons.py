import os
import sys
from pathlib import Path

# Adjust path to import root modules properly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Force UTF-8 encoding on standard output for Windows consoles to support emojis/Unicode
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# Import the tools
from server import (
    verify_workspace_fit,
    compose_solution_stack,
    get_repo_health,
    profile_repo_hardware_footprint,
    align_system_architecture,
    search_academic_papers
)

async def run_tests():
    """
    Executes mock verification tests for all major new addon tools.
    Performs dry-run checks against verify_workspace_fit, compose_solution_stack,
    get_repo_health, profile_repo_hardware_footprint, align_system_architecture,
    and search_academic_papers APIs.
    """
    # 1. Test workspace fit calculation
    print("=== Testing verify_workspace_fit ===")
    try:
        res = await verify_workspace_fit("psf/requests", ".")
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

    # 2. Test stack composer capability
    print("\n=== Testing compose_solution_stack ===")
    try:
        res = await compose_solution_stack("secure backend and local database", n_results=1)
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

    # 3. Test telemetry check
    print("\n=== Testing get_repo_health ===")
    try:
        res = await get_repo_health("psf/requests")
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

    # 4. Test microcontroller hardware footprinter
    print("\n=== Testing profile_repo_hardware_footprint ===")
    try:
        res = await profile_repo_hardware_footprint("lvgl/lvgl", "ESP32")
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

    # 5. Test architectural drift alignment
    print("\n=== Testing align_system_architecture ===")
    try:
        res = await align_system_architecture("SQLAlchemy", ".")
        print("SUCCESS:\n", res[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

    # 6. Test academic papers API integration (arXiv / Scholar)
    print("\n=== Testing search_academic_papers ===")
    try:
        res = await search_academic_papers("caching mechanisms", max_results=2)
        print("SUCCESS:\n", str(res)[:300], "\n...")
    except Exception as e:
        print("FAILED:", e)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_tests())

