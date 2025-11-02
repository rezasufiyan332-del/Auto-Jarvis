#!/usr/bin/env python3
"""
Use Python tokenizer to find unclosed braces
"""

import tokenize
import io

file_path = '/workspace/jarvis_project/jarvis_v14_ultimate/core/ultimate_termux_integration.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Tokenize and track braces
brace_stack = []
line_num = 1
token_num = 0

try:
    tokens = tokenize.generate_tokens(io.StringIO(content).readline)
    
    for tok in tokens:
        token_num += 1
        
        if tok.type == tokenize.OP:
            if tok.string == '{':
                brace_stack.append((tok.start[0], tok.string))
                if tok.start[0] >= 3180 and tok.start[0] <= 3200:
                    print(f"Line {tok.start[0]}: Opening {{ (stack size: {len(brace_stack)})")
            elif tok.string == '}':
                if brace_stack:
                    brace_stack.pop()
                    if tok.start[0] >= 3180 and tok.start[0] <= 3220:
                        print(f"Line {tok.start[0]}: Closing }} (stack size: {len(brace_stack)})")
                else:
                    print(f"❌ Line {tok.start[0]}: Unexpected closing }}")
                    
except tokenize.TokenError as e:
    print(f"\n❌ Tokenization error: {e}")
    print(f"Unclosed braces remaining: {len(brace_stack)}")
    if brace_stack:
        print("\nUnclosed braces at lines:")
        for line, char in brace_stack[-5:]:  # Show last 5
            print(f"  Line {line}: {char}")
            
print(f"\n✅ Total unclosed braces: {len(brace_stack)}")
if brace_stack:
    print("\nAll unclosed braces:")
    for line, char in brace_stack:
        print(f"  Line {line}: {char}")
