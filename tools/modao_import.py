# -*- coding: utf-8 -*-
"""
把 docs/modao/pages/ 下 13 个静态画板一次性导入墨刀（import_to_proto 多页 HTML）。
用法:
    set MODAO_TOKEN=你的墨刀令牌
    python tools/modao_import.py
令牌获取: modao.cc 登录后 头像菜单 -> 令牌设置 -> 生成 Token。
导入后返回 project_cid 与 prototype_url（编辑/预览链接）。
"""
import json, os, re, urllib.request

BASE = 'https://modao.cc/a2-mcp/api'
PAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         'docs', 'modao', 'pages')

def rpc(method, params, i=1, timeout=600):
    req = urllib.request.Request(BASE, data=json.dumps(
        {"jsonrpc": "2.0", "id": i, "method": method, "params": params}).encode('utf-8'),
        method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept', 'application/json, text/event-stream')
    req.add_header('modao-token', os.environ['MODAO_TOKEN'])
    resp = urllib.request.urlopen(req, timeout=timeout)
    body = resp.read().decode('utf-8', errors='ignore')
    m = re.search(r'data:\s*(\{.*\})\s*$', body, re.S)
    return json.loads(m.group(1) if m else body)

def get_content(r):
    c = (r.get('result') or {}).get('content') or (r.get('result') or {}).get('structuredContent')
    if isinstance(c, list):
        texts = [x.get('text', '') for x in c if x.get('type') == 'text']
        try:
            return json.loads(texts[-1]) if texts else {}
        except Exception:
            return {'raw_text': texts}
    return c or {}

def main():
    files = sorted(f for f in os.listdir(PAGES_DIR) if f.endswith('.html'))
    if not files:
        raise SystemExit('docs/modao/pages/ 下没有画板文件，先运行 tools/modao_build_pages.py')
    html_list = []
    for f in files:
        src = open(os.path.join(PAGES_DIR, f), encoding='utf-8').read()
        m = re.search(r'<title>([^<]+)</title>', src)
        html_list.append({'name': m.group(1) if m else f[:-5], 'html': src})
    print('导入 %d 个页面 ...' % len(html_list))
    r = rpc('tools/call', {'name': 'import_to_proto',
                           'arguments': {'html_list': html_list, 'client': 'claude-code'}})
    res = get_content(r)
    print(json.dumps({k: v for k, v in res.items()
                      if k in ('success', 'status', 'message', 'project_cid',
                               'prototype_url', 'imported_items', 'input_type')},
                     ensure_ascii=False, indent=1))
    if res.get('success'):
        print('预览链接:', res.get('prototype_url'))
        print('分享: 打开该链接 -> 右上角 分享 -> 链接分享 -> 任何人可查看')

if __name__ == '__main__':
    main()
