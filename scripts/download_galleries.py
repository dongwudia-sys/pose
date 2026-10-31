#!/usr/bin/env python3
"""Download all pose and costume reference images, NO filtering."""
import concurrent.futures, hashlib, json, os, re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PROXY = os.environ.get('GALLERY_PROXY')

def fetch(url):
    args = ['curl', '--fail', '--location', '--silent', '--show-error', '--retry', '3', '--connect-timeout', '15', '--max-time', '120']
    if PROXY:
        args += ['--proxy', PROXY]
    return subprocess.check_output(args + [url], stderr=subprocess.PIPE)

def job(item):
    path = ROOT / item['file']
    try:
        data = path.read_bytes() if path.exists() else fetch(item['url'])
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError('Response is not PNG')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return dict(item, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    except Exception as e:
        return dict(item, error=str(e))

def main():
    items, excluded = [], {}
    for kind in ('pose', 'costume'):
        base = f'https://ai-{kind}-gallery.pages.dev/'
        source = fetch(base).decode()
        match = re.search(r'const D\s*=\s*', source)
        records = json.JSONDecoder().raw_decode(source[match.end():])[0]
        # ========== 改动点：不再筛选，全部选中 ==========
        selected = records
        excluded[kind] = len(records) - len(selected)  # 现在excluded永远是0
        for r in selected:
            items.append({
                'kind': kind,
                'id': r['id'],
                'file': f"images/{kind}/{r['id']}.png",
                'url': base + r['原寸'],
                'metadata': r
            })

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for result in pool.map(job, items):
            results.append(result)
            if len(results) % 50 == 0:
                print(f'{len(results)}/{len(items)}', flush=True)

    manifest_path = ROOT / 'manifest.json'
    manifest_path.write_text(json.dumps({
        'sources': ['https://ai-pose-gallery.pages.dev/', 'https://ai-costume-gallery.pages.dev/'],
        'excluded': excluded,
        'images': results
    }, ensure_ascii=False, indent=2) + '\n')

    failures = [r for r in results if 'error' in r]
    stat = {
        'downloaded': len(results)-len(failures),
        'failed': len(failures),
        'bytes': sum(r.get('bytes',0) for r in results)
    }
    print(json.dumps(stat), flush=True)
    if failures:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
