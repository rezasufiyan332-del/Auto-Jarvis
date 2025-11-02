#!/usr/bin/env python3
"""
Extract and validate just the shortcuts dictionary
"""

import ast

# Read the file
with open('/workspace/jarvis_project/jarvis_v14_ultimate/core/ultimate_termux_integration.py', 'r') as f:
    lines = f.readlines()

# Extract lines 3214-3259 (shortcuts function)
shortcuts_section = ''.join(lines[3213:3259])  # Line numbers are 0-indexed

print("Shortcuts section extracted:")
print("="*60)
print(shortcuts_section)
print("="*60)

# Try to parse just the function
try:
    ast.parse(shortcuts_section)
    print("\n✅ Shortcuts function syntax is valid")
except SyntaxError as e:
    print(f"\n❌ Syntax error in shortcuts function:")
    print(f"   Line {e.lineno}: {e.msg}")
    if e.text:
        print(f"   Code: {e.text.strip()}")
