content = open('utils.py', 'r', encoding='utf-8').read()
content = content.replace('[data-testid="stSidebar"]    { display:none !important; }', '')
with open('utils.py', 'w', encoding='utf-8') as f:
    f.write(content)
