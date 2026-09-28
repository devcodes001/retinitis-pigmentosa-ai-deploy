with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

checks = ['gayathri', 'gmail', 'github.com', 'huggingface.co']
for c in checks:
    found = c.lower() in content.lower()
    status = 'FOUND - needs fix' if found else 'REMOVED OK'
    print(c + ': ' + status)
