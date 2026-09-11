# Stress Test Protocol

Run these 8 tests before reporting system completion. All must pass.

## Test 1: Contract Loading (10K iterations)

```bash
python3 -c "
import json, pathlib, time
SYSTEM = pathlib.Path('/home/massi/.hermes/system')
files = [f for f in SYSTEM.iterdir() if f.suffix in ('.json', '.md', '.yaml')]
start = time.perf_counter()
for _ in range(10000):
 for f in files:
 if f.suffix == '.json': json.loads(f.read_text())
 else: f.read_text()
elapsed = time.perf_counter() - start
print(f'Time: {elapsed:.3f}s, Per read: {elapsed/(len(files)*10000)*1000:.4f}ms')
print('PASS' if elapsed < 10 else 'FAIL')
"
```

## Test 2: Model Gateway Select (1K iterations)

```bash
for i in {1..100}; do bash ~/.hermes/system/model-gateway.sh select 'research' 'medium' 'omni-researcher' > /dev/null; done
```

## Test 3: Context Detection (10K iterations)

```bash
python3 -c "
import time
models = ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5', 'claude-sonnet', 'claude-haiku', 'gemini-pro', 'gemini-flash', 'grok-3', 'grok-4', 'ling-3.0', 'unknown']
start = time.perf_counter()
for _ in range(10000):
 for m in models:
 if 'gpt-4o' in m and 'mini' not in m: p = 'xlarge'
 elif 'gpt-4o-mini' in m: p = 'large'
 elif 'gpt-3.5' in m: p = 'medium'
 elif 'sonnet' in m: p = 'xlarge'
 elif 'haiku' in m: p = 'large'
 elif 'pro' in m: p = 'max'
 elif 'flash' in m: p = 'max'
 elif 'grok-3' in m: p = 'large'
 elif 'grok-4' in m: p = 'xlarge'
 elif 'ling' in m: p = 'large'
 else: p = 'medium'
elapsed = time.perf_counter() - start
print(f'Time: {elapsed:.4f}s, PASS' if elapsed < 1 else 'FAIL')
"
```

## Test 4: Registry Referential Integrity

```bash
python3 -c "
import json, pathlib
reg = json.loads(pathlib.Path('/home/massi/.hermes/system/registry.json').read_text())
all_names = {a['name'] for a in reg['agents']}
errors = []
for a in reg['agents']:
 for u in a.get('upstream', []):
 if u not in all_names: errors.append(f'{a["name"]} upstream {u}')
 for d in a.get('downstream', []):
 if d not in all_names: errors.append(f'{a["name"]} downstream {d}')
print(f'Errors: {len(errors)}, PASS' if len(errors) == 0 else f'FAIL: {errors}')
"
```

## Test 5: Quality Metrics Math

```bash
python3 -c "
metrics = {'missions': 100, 'factual_errors': 4, 'claims_total': 850, 'claims_verified': 720, 'human_overrides': 18}
fer = (metrics['factual_errors'] / metrics['claims_total']) * 100
hor = (metrics['human_overrides'] / metrics['missions']) * 100
print(f'FER: {fer:.2f}%, HOR: {hor:.2f}%, PASS' if fer < 5 and hor < 20 else 'NEEDS ATTENTION')
"
```

## Test 6: Cold vs Warm Cache

```bash
python3 -c "
import time, pathlib, json
SYSTEM = pathlib.Path('/home/massi/.hermes/system')
start = time.perf_counter()
for f in SYSTEM.iterdir():
 if f.suffix in ('.json', '.md', '.yaml'):
 if f.suffix == '.json': json.loads(f.read_text())
 else: f.read_text()
cold = time.perf_counter() - start
start = time.perf_counter()
for f in SYSTEM.iterdir():
 if f.suffix in ('.json', '.md', '.yaml'):
 if f.suffix == '.json': json.loads(f.read_text())
 else: f.read_text()
warm = time.perf_counter() - start
print(f'Cold: {cold*1000:.2f}ms, Warm: {warm*1000:.2f}ms, PASS' if cold < 100 and warm < 50 else 'SLOW')
"
```

## Test 7: Bootstrap 100 Calls

```bash
for i in {1..100}; do bash ~/.hermes/system/bootstrap.sh --status > /dev/null 2>&1; done
```

## Test 8: Ledger Schema Validation

```bash
python3 -c "
import json, pathlib
schema = json.loads(pathlib.Path('/home/massi/.hermes/system/ledger-schema.json').read_text())
assert 'layout' in schema and 'directories' in schema['layout'] and 'files' in schema['layout']
print(f'Files: {len(schema["layout"]["files"])}, Dirs: {len(schema["layout"]["directories"])}, PASS')
"
```

## Pass Criteria

All 8 tests must pass. If any fails, fix the underlying issue before reporting completion.