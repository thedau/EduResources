import re, glob, os

def fix_split_vars(content):
    """Fix {{ variable }} tags split across multiple lines by Prettier."""
    # Match {{ ... }} spanning multiple lines
    content = re.sub(r'\{\{([^}]*?\n[^}]*?)\}\}', lambda m: '{{ ' + ' '.join(m.group(1).split()) + ' }}', content)
    return content

def fix_split_tags(content):
    """Fix {% ... %} tags split across multiple lines."""
    content = re.sub(r'\{%([^%]*?\n[^%]*?)%\}', lambda m: '{% ' + ' '.join(m.group(1).split()) + ' %}', content)
    return content

count = 0
for path in glob.glob('templates/**/*.html', recursive=True):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    # Run multiple passes
    for _ in range(3):
        content = fix_split_vars(content)
        content = fix_split_tags(content)
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1
        print(f'FIXED: {os.path.relpath(path)}')

print(f'\nFixed {count} files. Validating...')

import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'eduresource.settings'
django.setup()
from django.template.loader import get_template

errors = 0
for root, dirs, files in os.walk('templates'):
    for f in files:
        if f.endswith('.html'):
            rel = os.path.relpath(os.path.join(root, f), 'templates').replace('\\','/')
            try:
                get_template(rel)
            except Exception as e:
                errors += 1
                print(f'  ERR: {rel} -> {str(e).splitlines()[0]}')

if errors == 0:
    print('All templates valid!')
else:
    print(f'{errors} template error(s)!')
