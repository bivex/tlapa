with open("example/distributed_log_full.tla", "r") as f:
    content = f.read()

# Simple count
open_cnt = content.count("(")
close_cnt = content.count(")")
print(f"Total '(': {open_cnt}, total ')': {close_cnt}")
if open_cnt == close_cnt:
    print("Parentheses balanced")
else:
    print(f"Difference: {open_cnt - close_cnt}")

# Also check for unmatched by scanning lines
stack = []
for i, ch in enumerate(content, 1):
    if ch == "(":
        stack.append(i)
    elif ch == ")":
        if stack:
            stack.pop()
        else:
            print(f"Unmatched closing ) at char {i}")
if stack:
    print(f"Unmatched opening ( at chars: {stack}")
