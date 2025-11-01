#!/usr/bin/env python3
"""
removeAll.py - Remove all RNBO modules from Percussa SSP/XMX project

This script removes all modules by:
1. Finding all existing modules
2. Confirming with the user (destructive operation)
3. Using removeModule.py to remove each module

Compatible with Windows, macOS, and Linux.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List


def get_project_root() -> Path:
    """Get the project root directory"""
    script_dir = Path(__file__).parent
    return script_dir.parent.parent


def list_available_modules(modules_dir: Path) -> List[str]:
    """List all available modules in the modules directory"""
    modules = []
    for item in modules_dir.iterdir():
        if item.is_dir() and item.name not in ['common', 'inc', '.git']:
            modules.append(item.name)
    return sorted(modules)


def confirm_removal(modules: List[str], force: bool = False) -> bool:
    """Confirm with user that they want to remove all modules"""
    if force:
        return True
    
    if not modules:
        print("No modules found to remove.")
        return False
    
    print(f"\nWARNING: This will permanently delete ALL {len(modules)} modules:")
    for module in modules:
        print(f"  - {module}")
    print("\nThis action cannot be undone!")
    
    while True:
        response = input(f"\nAre you sure you want to remove ALL {len(modules)} modules? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def remove_all_modules(modules: List[str], project_root: Path) -> bool:
    """Remove all modules using removeModule.py"""
    remove_script = project_root / "scripts" / "removeModule.py"
    
    if not remove_script.exists():
        print(f"Error: removeModule.py not found at {remove_script}")
        return False
    
    success_count = 0
    total_count = len(modules)
    
    for module in modules:
        print(f"\nRemoving module '{module}'...")
        try:
            # Use the removeModule.py script with --force flag
            result = subprocess.run([
                sys.executable, str(remove_script), module, "--force"
            ], capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                print(f"Successfully removed '{module}'")
                success_count += 1
            else:
                print(f"Failed to remove '{module}': {result.stderr}")
        except Exception as e:
            print(f"Error removing '{module}': {e}")
    
    print(f"\nRemoval complete: {success_count}/{total_count} modules removed successfully")
    return success_count == total_count


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Remove all RNBO modules from Percussa SSP/XMX project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with confirmation
  python removeAll.py
  
  # Remove all modules without confirmation (dangerous!)
  python removeAll.py --force
  
WARNING: This operation is destructive and cannot be undone!
        """
    )
    
    parser.add_argument('--force', action='store_true',
                       help='Remove all modules without confirmation (dangerous!)')
    
    args = parser.parse_args()
    
    # Get project directories
    project_root = get_project_root()
    modules_dir = project_root / "modules"
    
    # Validate directories exist
    if not modules_dir.exists():
        print(f"Error: Modules directory {modules_dir} not found!")
        sys.exit(1)
    
    # List available modules
    available_modules = list_available_modules(modules_dir)
    
    if not available_modules:
        print("No modules found to remove.")
        sys.exit(0)
    
    # Confirm removal
    if not confirm_removal(available_modules, args.force):
        print("Removal cancelled.")
        sys.exit(0)
    
    # Remove all modules
    success = remove_all_modules(available_modules, project_root)
    
    if success:
        print("\nAll modules have been successfully removed!")
        print("\nYou may want to clean your build directory:")
        if os.name == 'nt':  # Windows
            print("   rmdir /s build*")
        else:  # Unix-like (macOS, Linux)
            print("   rm -rf build*/")
    else:
        print("\nSome modules could not be removed. Please check manually.")
        sys.exit(1)


if __name__ == "__main__":
    main()