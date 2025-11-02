#!/usr/bin/env python3
"""
Find unclosed brackets in a Python file
"""

import sys

file_path = '/workspace/jarvis_project/jarvis_v14_ultimate/core/ultimate_termux_integration.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    
# Count brackets
open_braces = content.count('{')
close_braces = content.count('}')
open_brackets = content.count('[')
close_brackets = content.count(']')
open_parens = content.count('(')
close_parens = content.count(')')

print(f"Bracket Analysis for {file_path}:")
print(f"  {{ (open):  {open_braces}")
print(f"  }} (close): {close_braces}")
print(f"  Difference: {open_braces - close_braces}")
print()
print(f"  [ (open):  {open_brackets}")
print(f"  ] (close): {close_brackets}")
print(f"  Difference: {open_brackets - close_brackets}")
print()
print(f"  ( (open):  {open_parens}")
print(f"  ) (close): {close_parens}")
print(f"  Difference: {open_parens - close_parens}")

# Find the problematic section
lines = content.split('\n')
brace_count = 0
bracket_count = 0
paren_count = 0

print("\nLine-by-line brace tracking (showing only non-zero):")
for i, line in enumerate(lines[:3250], 1):
    # Count in strings can be misleading, but let's try
    line_open_braces = line.count('{')
    line_close_braces = line.count('}')
    
    brace_count += line_open_braces - line_close_braces
    
    if line_open_braces > 0 or line_close_braces > 0:
        print(f"  Line {i}: {line_open_braces} open, {line_close_braces} close, total: {brace_count} | {line.strip()[:80]}")
        
if brace_count != 0:
    print(f"\n❌ Unclosed braces detected! Total unclosed: {brace_count}")
else:
    print(f"\n✅ All braces balanced in first 3250 lines")
