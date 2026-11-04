"""Measure committed sizes: files over the cap and per-task totals (T065)."""
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
raw = subprocess.run(['git', 'ls-files', '-z'], capture_output=True, check=True).stdout
files = []
total = 0
per_task = {}
for name in raw.decode('utf-8', 'surrogateescape').split('\0'):
    if not name:
        continue
    p = Path(name)
    if not p.is_file():
        continue
    size = p.stat().st_size
    total += size
    files.append((name, size))
    parts = p.parts
    if len(parts) > 1 and parts[0] == 'experiments':
        task = parts[1].split('-')[0]
        per_task[task] = per_task.get(task, 0) + size

files.sort(key=lambda x: -x[1])
report = {
    'tracked_files': len(files),
    'tracked_bytes': total,
    'cap_file_bytes': 2 * 1024 * 1024,
    'cap_task_bytes': 10 * 1024 * 1024,
    'files_over_file_cap': [{'path': n, 'bytes': s} for n, s in files if s > 2 * 1024 * 1024],
    'tasks_over_task_cap': {t: s for t, s in sorted(per_task.items(), key=lambda kv: -kv[1])
                            if s > 10 * 1024 * 1024},
    'largest_tasks': [{'task': t, 'bytes': s} for t, s in
                      sorted(per_task.items(), key=lambda kv: -kv[1])[:5]],
    'largest_files': [{'path': n, 'bytes': s} for n, s in files[:5]],
}
out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
text = json.dumps(report, indent=2) + '\n'
if out:
    out.write_text(text, encoding='utf-8')
print(text)
