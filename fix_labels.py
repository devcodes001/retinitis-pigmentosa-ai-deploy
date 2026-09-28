with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Swap labels: Disease=0, Normal=1 (to match training class mapping)
lines[249] = '                    0: "\U0001f534 Disease Detected",\n'
lines[250] = '                    1: "\U0001f7e2 Normal (Healthy)"\n'

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Done! Verifying...')
with open('app.py', 'r', encoding='utf-8') as f:
    content_lines = f.readlines()
print(repr(content_lines[248]))
print(repr(content_lines[249]))
print(repr(content_lines[250]))
