"""Audit the Git index, not merely .gitignore or the working tree."""
import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBMODULES = {'psxrecomp', 'references/rood-reverse', 'references/pcsx-redux'}
PRIVATE = {'local', 'build', 'generated', '.venv', 'cache', 'bios', 'saves', 'dist', 'artifacts'}
BLOCKED_SUFFIXES = {'.bin', '.cue', '.iso', '.chd', '.exe', '.dll', '.mcd', '.pst', '.thumb', '.zip', '.raw', '.png', '.jpg'}
PATTERNS = {
    'private key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'GitHub credential': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    'API credential': re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b'),
    'credential in URL': re.compile(r'https?://[^\s/@:]+:[^\s/@]+@'),
    'personal absolute path': re.compile(r'(?:[A-Za-z]:[/\\]Users[/\\]|/Users/|/home/)[\w .@-]+[/\\]'),
}

def audit_blob(path, data):
    issues = []
    file = Path(path)
    if file.parts[0] in PRIVATE or file.suffix.lower() in BLOCKED_SUFFIXES:
        issues.append('private/generated/media artifact')
    if file.name == '.env' or file.name.startswith('.env.') and file.name != '.env.example':
        issues.append('environment file')
    if len(data) > 512 * 1024:
        issues.append('unexpected large file')
    if b'\0' in data:
        issues.append('binary content')
    try:
        content = data.decode('utf-8-sig')
    except UnicodeDecodeError:
        return issues + ['non-UTF-8 content']
    for label, pattern in PATTERNS.items():
        if pattern.search(content):
            issues.append(label)
    if re.search(r'"bytes_b64"\s*:', content):
        issues.append('embedded game capture payload')
    return issues

def self_test():
    assert not audit_blob('README.md', b'No private data. SHA1: abc123')
    assert audit_blob('local/game.bin', b'payload')
    assert audit_blob('tools/sample.py', b'x\0y')
    assert audit_blob('settings.txt', ('ghp_' + 'A' * 36).encode())
    assert audit_blob('settings.txt', ('C:' + '/Users/' + 'example/file').encode())
    print('Audit self-test: 5 checks passed')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    index = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=ROOT)
    errors = []
    files = modules = total = 0
    for row in index.split(b'\0'):
        if not row:
            continue
        meta, name = row.split(b'\t', 1)
        mode, object_id, stage = meta.decode().split()
        path = name.decode('utf-8')
        if stage != '0':
            errors.append((path, ['unresolved index stage']))
        if mode == '160000':
            modules += 1
            if path not in SUBMODULES:
                errors.append((path, ['unexpected submodule']))
            continue
        if mode != '100644' and mode != '100755':
            errors.append((path, ['unexpected file mode']))
            continue
        data = subprocess.check_output(['git', 'cat-file', 'blob', object_id], cwd=ROOT)
        files += 1
        total += len(data)
        issues = audit_blob(path, data)
        if issues:
            errors.append((path, issues))
    if not files:
        errors.append(('<index>', ['no source files staged']))
    for path, issues in errors:
        print(f'{path}: {", ".join(issues)}')
    print(f'Index audit: {files} text files, {modules} submodules, {total} bytes, {len(errors)} findings')
    raise SystemExit(bool(errors))

if __name__ == '__main__':
    main()
