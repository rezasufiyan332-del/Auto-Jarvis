#!/usr/bin/env python3
"""
Binary search to find where syntax error starts
"""

import py_compile
import tempfile
import os

file_path = '/workspace/jarvis_project/jarvis_v14_ultimate/core/ultimate_termux_integration.py'

with open(file_path, 'r') as f:
    all_lines = f.readlines()

total_lines = len(all_lines)
print(f"Total lines in file: {total_lines}")

def test_lines(n):
    """Test if first n lines compile"""
    content = ''.join(all_lines[:n])
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        py_compile.compile(tmp_path, doraise=True)
        os.unlink(tmp_path)
        return True
    except SyntaxError:
        os.unlink(tmp_path)
        return False
    except Exception:
        os.unlink(tmp_path)
        return True  # Other errors are OK for partial files

# Binary search to find the problematic line
left, right = 1, total_lines
last_good = 0

print("\nBinary searching for first syntax error...")

while left <= right:
    mid = (left + right) // 2
    
    if test_lines(mid):
        last_good = mid
        left = mid + 1
        print(f"  Lines 1-{mid}: ✅ OK")
    else:
        right = mid - 1
        print(f"  Lines 1-{mid}: ❌ Error")

print(f"\n✅ Last good line: {last_good}")
print(f"❌ First error around line: {last_good + 1}")

if last_good + 1 <= total_lines:
    print(f"\nLines around the error ({last_good}-{min(last_good+5, total_lines)}):")
    for i in range(last_good, min(last_good + 5, total_lines)):
        print(f"  {i+1}: {all_lines[i].rstrip()}")
