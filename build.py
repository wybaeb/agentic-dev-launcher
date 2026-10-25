#!/usr/bin/env python3
"""src/index.html -> docs/index.html, зашифрованный: gzip -> AES-256-GCM, ключ = PBKDF2-SHA256(пароль, соль, 200000).
Пароль: $LAUNCHER_PASSWORD. Соль постоянная (docs/salt.b64), IV новый на каждую сборку."""
import base64, gzip, hashlib, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
ROOT = os.path.dirname(os.path.abspath(__file__)); ITER = 200000
pw = os.environ.get('LAUNCHER_PASSWORD', '').strip() or sys.exit('нет $LAUNCHER_PASSWORD')
sp = os.path.join(ROOT, 'docs', 'salt.b64')
if not os.path.exists(sp):
    open(sp, 'w').write(base64.b64encode(os.urandom(16)).decode())
salt = base64.b64decode(open(sp).read().strip())
key = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt, ITER, 32)
html = open(os.path.join(ROOT, 'src', 'index.html'), encoding='utf-8').read()
iv = os.urandom(12)
payload = AESGCM(key).encrypt(iv, gzip.compress(html.encode('utf-8'), 9), None)
shell = open(os.path.join(ROOT, 'shell.html'), encoding='utf-8').read()
title = re.search(r'<title>(.*?)</title>', html).group(1)
out = (shell.replace('__PAYLOAD__', base64.b64encode(payload).decode()).replace('__SALT__', base64.b64encode(salt).decode())
       .replace('__IV__', base64.b64encode(iv).decode()).replace('__ITER__', str(ITER)).replace('__TITLE__', title))
open(os.path.join(ROOT, 'docs', 'index.html'), 'w', encoding='utf-8').write(out)
open(os.path.join(ROOT, 'docs', '.nojekyll'), 'w').close()
print('docs/index.html:', len(out) // 1024, 'КБ')
