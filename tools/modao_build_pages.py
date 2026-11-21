# -*- coding: utf-8 -*-
"""
把 HTML 高保真原型渲染为 13 个独立静态页面（含真实互跳链接），
供墨刀 import_to_proto 多页导入。
用法: python tools/modao_build_pages.py
"""
import os, re, subprocess, sys

ROOT = r'D:\Desktop\软件工程\factlens-team-repo'
PROTO = os.path.join(ROOT, 'docs', 'prototype')
OUT = os.path.join(ROOT, 'docs', 'modao', 'pages')
TMP = os.path.join(ROOT, 'tools', 'modao_tmp')
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

from bs4 import BeautifulSoup

CSS = open(os.path.join(PROTO, 'assets', 'style.css'), encoding='utf-8').read()
CSS_EXTRA = """
/* 墨刀静态页导出补充：按钮链接化 */
a.btn{text-decoration:none;display:inline-block;box-sizing:border-box;line-height:1.4}
a.checking-panel{display:block;text-decoration:none;cursor:pointer}
"""

# (输出文件名, 源文件, hash 参数, 页面标题)
PAGES = [
    ('p01-front-home',        'index.html', '#home?fill=0',              '1-前台-核查页'),
    ('p02-front-checking',    'index.html', '#home?checking=1',          '2-前台-核查中'),
    ('p03-front-report',      'index.html', '#home?demo=1',              '3-前台-核查报告'),
    ('p04-front-history',     'index.html', '#history?seed=1',           '4-前台-历史记录'),
    ('p05-front-about',       'index.html', '#about',                    '5-前台-关于'),
    ('p06-admin-login',       'admin.html', '',                           '6-后台-登录'),
    ('p07-admin-overview',    'admin.html', '#overview?demo=1',          '7-后台-数据概览'),
    ('p08-admin-records',     'admin.html', '#records?demo=1',           '8-后台-核查记录'),
    ('p08b-admin-drawer',     'admin.html', '#records?demo=1&open=drawer', '8b-后台-记录详情抽屉'),
    ('p08c-admin-confirm',    'admin.html', '#records?demo=1&open=confirm', '8c-后台-删除确认'),
    ('p09-admin-sources',     'admin.html', '#sources?demo=1',           '9-后台-证据源管理'),
    ('p09b-admin-source-modal','admin.html', '#sources?demo=1&open=source', '9b-后台-新增证据源'),
    ('p10-admin-config',      'admin.html', '#config?demo=1',            '10-后台-系统配置'),
]

def dump(file, hashpart, budget=7000):
    url = 'file:///' + os.path.join(PROTO, file).replace('\\', '/') + hashpart
    profile = os.path.join(TMP, 'ep_' + re.sub(r'\W', '_', hashpart) + '_' + file)
    cmd = [EDGE, '--headless=new', '--disable-gpu', '--no-first-run',
           '--virtual-time-budget=%d' % budget, '--user-data-dir=' + profile,
           '--dump-dom', url]
    p = subprocess.run(cmd, capture_output=True, timeout=180)
    out = p.stdout.decode('utf-8', errors='ignore')
    if 'page-home' not in out and 'login-view' not in out:
        sys.stderr.write('[warn] dump of %s%s looks empty (%d bytes)\n' % (file, hashpart, len(out)))
    return out

def to_link(tag, href):
    """把 button 转成 <a>，便于墨刀导入时识别为跳转热点。"""
    tag.name = 'a'
    tag['href'] = href
    for a in ('type', 'disabled', 'data-detail', 'data-del'):
        if tag.has_attr(a):
            del tag[a]
    return tag

def strip_hidden(soup):
    """删除带 inline display:none 的元素（.show 状态的弹层不受影响）。先收集后删除，
    避免 bs4 html.parser 在迭代中 decompose 产生 attrs=None 的残留元素。"""
    victims = []
    for el in soup.find_all(style=True):
        if el.attrs is None or el.name is None:
            continue
        st = el.get('style', '')
        if re.search(r'display\s*:\s*none', st):
            victims.append(el)
    for v in victims:
        v.decompose()

def build_page(name, file, hashpart, title):
    raw = dump(file, hashpart)
    soup = BeautifulSoup(raw, 'html.parser')
    # ---- head：内联 CSS + 标题 ----
    for ln in soup.find_all('link'):
        ln.decompose()
    st = soup.new_tag('style')
    st.string = CSS + CSS_EXTRA
    soup.head.append(st)
    t = soup.find('title')
    t.string = title
    # ---- 移除脚本 ----
    for s in soup.find_all('script'):
        s.decompose()
    # ---- 移除 toast ----
    for s in soup.select('.toast'):
        s.decompose()

    is_admin = file == 'admin.html'

    if not is_admin:
        # ============ 前台 ============
        body = soup.body
        # 只保留目标视图，删掉其余 .page
        if name in ('p01-front-home', 'p02-front-checking', 'p03-front-report'):
            keep = 'page-home'
            # 页面内部的取舍
            if name == 'p02-front-checking':
                for c in body.select('.check-card'):
                    c.decompose()
                for r in body.select('#report-card'):
                    r.decompose()
                panel = body.select_one('#checking-panel')
                if panel:
                    panel.name = 'a'
                    panel['href'] = 'p03-front-report.html'
            elif name == 'p03-front-report':
                for c in body.select('.check-card'):
                    c.decompose()
                for c in body.select('#checking-panel'):
                    c.decompose()
                recheck = body.select_one('#btn-recheck')
                if recheck:
                    to_link(recheck, 'p01-front-home.html')
            else:  # p01
                for r in body.select('#report-card, #checking-panel'):
                    r.decompose()
                btn = body.select_one('#btn-check')
                if btn:
                    to_link(btn, 'p02-front-checking.html')
        else:
            keep = {'p04-front-history': 'page-history', 'p05-front-about': 'page-about'}[name]
            if name == 'p04-front-history':
                for r in body.select('#history-list [data-recheck]'):
                    to_link(r, 'p01-front-home.html')
                # 删除按钮保留为静态按钮（无链接）
        for sec in body.select('main .page'):
            if sec.get('id') != keep:
                sec.decompose()
        # 导航链接重写
        navmap = {'home': 'p01-front-home.html', 'history': 'p04-front-history.html',
                  'about': 'p05-front-about.html'}
        for a in body.select('.nav a, a.logo'):
            h = (a.get('href') or '').lstrip('#').split('?')[0]
            if h in navmap:
                a['href'] = navmap[h]
        for a in body.select('.site-footer a, .empty-state a'):
            a['href'] = 'p01-front-home.html'
    else:
        # ============ 后台 ============
        body = soup.body
        if name == 'p06-admin-login':
            for sh in body.select('#admin-shell'):
                sh.decompose()
            btn = body.select_one('#btn-login')
            if btn:
                to_link(btn, 'p07-admin-overview.html')
        else:
            for lv in body.select('#login-view'):
                lv.decompose()
            keep = {'p07-admin-overview': 'page-overview',
                    'p08-admin-records': 'page-records',
                    'p08b-admin-drawer': 'page-records',
                    'p08c-admin-confirm': 'page-records',
                    'p09-admin-sources': 'page-sources',
                    'p09b-admin-source-modal': 'page-sources',
                    'p10-admin-config': 'page-config'}[name]
            for sec in body.select('.admin-page'):
                if sec.get('id') != keep:
                    sec.decompose()
            # 侧边栏菜单
            sidemap = {'overview': 'p07-admin-overview.html', 'records': 'p08-admin-records.html',
                       'sources': 'p09-admin-sources.html', 'config': 'p10-admin-config.html'}
            for a in body.select('.side-menu a'):
                h = (a.get('href') or '').lstrip('#')
                if h in sidemap:
                    a['href'] = sidemap[h]
            for a in body.select('#btn-logout'):
                a['href'] = 'p06-admin-login.html'
            # 表格操作按钮 → 弹层画板
            for d in body.select('[data-detail]'):
                to_link(d, 'p08b-admin-drawer.html')
            for d in body.select('[data-del]'):
                to_link(d, 'p08c-admin-confirm.html')
            for e in body.select('[data-edit]'):
                to_link(e, 'p09b-admin-source-modal.html')
            for b in body.select('#btn-add-source'):
                to_link(b, 'p09b-admin-source-modal.html')
            # 弹层画板：关闭/取消/保存按钮 → 回到对应页
            if name == 'p08b-admin-drawer':
                for c in body.select('#drawer-close'):
                    to_link(c, 'p08-admin-records.html')
            elif name == 'p08c-admin-confirm':
                for c in body.select('#confirm-cancel'):
                    to_link(c, 'p08-admin-records.html')
                for c in body.select('#confirm-ok'):
                    to_link(c, 'p08-admin-records.html')
            elif name == 'p09b-admin-source-modal':
                for c in body.select('#source-cancel, #source-save'):
                    to_link(c, 'p09-admin-sources.html')
            # 其他页的隐藏弹层清掉
            if name not in ('p08b-admin-drawer',):
                for d in body.select('#detail-drawer'):
                    if 'show' not in (d.get('class') or []):
                        d.decompose()
            if name not in ('p08c-admin-confirm',):
                for m in body.select('#confirm-mask'):
                    if 'show' not in (m.get('class') or []):
                        m.decompose()
            if name not in ('p09b-admin-source-modal',):
                for m in body.select('#source-mask'):
                    if 'show' not in (m.get('class') or []):
                        m.decompose()

    strip_hidden(soup)
    out_path = os.path.join(OUT, name + '.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n' + str(soup))
    return out_path, len(raw)

def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    for name, f, h, title in PAGES:
        try:
            path, n = build_page(name, f, h, title)
            print('OK  %-26s %6d -> %s' % (name, n, path))
        except Exception as e:
            print('ERR %-26s %s' % (name, e))

if __name__ == '__main__':
    main()
