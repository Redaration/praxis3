#!/usr/bin/env python3
"""
This script renames Python files in a directory to add a prefix.

Usage as a script (renames files in the current directory with prefix 'a'):
    python rename_files.py

Usage as a module:
    from rename_files import rename_files_with_prefix
    rename_files_with_prefix("/path/to/your/dir", "your_prefix_")
"""
import os
import sys

def rename_files_with_prefix(directory, prefix):
    """
    Rename all Python files in the directory to have the specified prefix.
    """
    print(f"Renaming Python files in {directory} to have prefix '{prefix}'...")
    
    # Get all Python files in the current directory (no subdirectories)
    python_files = [f for f in os.listdir(directory) if f.endswith('.py') and os.path.isfile(os.path.join(directory, f))]
    
    # Skip this script itself to avoid renaming it during execution
    this_script = os.path.basename(__file__)
    if this_script in python_files:
        python_files.remove(this_script)
    
    print(f"Found {len(python_files)} Python files to rename:")
    for file in python_files:
        print(f"  {file}")
    
    # Confirm before proceeding
    print("\nWill add prefix to all these files.")
    
    # Rename files
    renamed_files = []
    for old_name in python_files:
        if old_name.startswith(prefix):
            print(f"Skipping {old_name} as it already has the prefix")
            continue
            
        new_name = f"{prefix}{old_name}"
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        
        print(f"Renaming: {old_name} -> {new_name}")
        os.rename(old_path, new_path)
        renamed_files.append((old_name, new_name))
    
    print(f"\nRenamed {len(renamed_files)} files:")
    for old, new in renamed_files:
        print(f"  {old} -> {new}")
    
    return renamed_files

if __name__ == "__main__":
    # Use the current directory
    current_dir = os.getcwd()
    rename_files_with_prefix(current_dir, "a")
