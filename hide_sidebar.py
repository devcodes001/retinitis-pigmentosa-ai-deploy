content = open('utils.py', 'r', encoding='utf-8').read()
content = content.replace('[data-testid="stSidebarNav"] { display:none !important; }', '[data-testid="stSidebarNav"] { display:none !important; }\n[data-testid="stSidebar"]    { display:none !important; }')
open('utils.py', 'w', encoding='utf-8').write(content)
