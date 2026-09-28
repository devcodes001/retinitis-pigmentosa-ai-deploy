content = open('app.py', 'r', encoding='utf-8').read()
content = content.replace('<div class="f-brand">RP EYECARE<span>AI</span></div>', '<div class="f-brand">RP <span>EYECARE</span></div>')
open('app.py', 'w', encoding='utf-8').write(content)
