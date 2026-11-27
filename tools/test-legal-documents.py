#!/usr/bin/env python3
"""Check legal page routes and the current approved document structure offline."""
import json
import re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ('rules', 'contraindications', 'privacy', 'contacts', 'consent')


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links = []
        self.headings = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if tag == 'h1':
            self.headings += 1


def main():
    pages = {slug: (ROOT / 'documents' / slug / 'index.html').read_text() for slug in SLUGS}
    footer = (ROOT / 'src/components/Footer.astro').read_text()
    assert re.findall(r'<a href="(/documents/[^\"]+)">([^<]+)</a>', footer) == [
        ('/documents/contacts/', 'Реквизиты'),
        ('/documents/contraindications/', 'Противопоказания'),
        ('/documents/privacy/', 'Политика конфиденциальности'),
        ('/documents/rules/', 'Правила записи и оказания услуг'),
    ]
    for slug, source in pages.items():
        page = Page(source)
        assert page.headings == 1, slug
        assert f'https://denisyuce.com/documents/{slug}/' in source, slug
        if slug in ('privacy', 'consent'):
            assert '773123178360' in source and 'mailto:info@denisyuce.com' in source, slug
        assert 'Редакция от 06.11.2026.' not in source, slug
        assert 'DIKIDI' not in source, slug
        assert not re.search(r'паспорт гражданина|ключ\s*:\s*\d|CLOUDFLARE_API_TOKEN', source, re.I), slug
        if slug == 'consent':
            assert 'href="/documents/consent/"' not in footer
        else:
            assert f'href="/documents/{slug}/"' in footer, slug
        for href in page.links:
            assert href and href == href.strip(), (slug, href)
            url = urlsplit(href)
            assert url.scheme in ('', 'https', 'mailto', 'tel'), (slug, href)
            if url.scheme == 'mailto':
                assert url.path == 'info@denisyuce.com', (slug, href)
            if url.scheme == 'tel':
                assert url.path == '+79951568066', (slug, href)
            if not url.netloc or url.netloc == 'denisyuce.com':
                if url.scheme in ('mailto', 'tel'):
                    continue
                assert url.path.startswith('/'), (slug, href)
                if url.path.startswith('/documents/'):
                    target = ROOT / url.path.lstrip('/') / 'index.html'
                    assert target.is_file(), (slug, href)
                    if url.fragment:
                        assert f'id="{unquote(url.fragment)}"' in target.read_text(), (slug, href)
                    if (ROOT / 'dist').exists():
                        assert (ROOT / 'dist' / url.path.lstrip('/') / 'index.html').is_file(), (slug, href)

        for schema in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', source, re.S):
            json.loads(schema)
        built = ROOT / 'dist/documents' / slug / 'index.html'
        if built.exists():
            rendered = built.read_text()
            assert '<header class="site-header">' in rendered and '<footer>' in rendered, slug
            article = re.search(r'<article class="privacy-text">(.*?)</article>', source, re.S)[1]
            for paragraph in re.findall(r'<(?:p|h2|h3|li)>(.*?)</(?:p|h2|h3|li)>', article, re.S):
                assert paragraph in rendered, (slug, paragraph)

    rules = pages['rules']
    assert re.findall(r'<h2>(.*?)</h2>', rules) == [
        '1. Общие положения', '2. Запись, отмена и перенос', '3. Условия оказания услуг',
        '4. Стоимость и оплата', '5. Абонементы', '6. Заключительные положения',
    ]
    for section, count in [(1, 5), (2, 9), (3, 5), (4, 4), (5, 8), (6, 4)]:
        assert re.findall(rf'<p>({section}\.\d+)\.', rules) == [f'{section}.{n}' for n in range(1, count + 1)]
    assert 'полную или частичную предварительную оплату' in rules
    assert 'прейскуранту, действующему на дату отказа' in rules
    assert 'до 22:00 дня, предшествующего дню оказания услуги' in rules
    assert 'применяется к договорам, заключённым после вступления её в силу' in rules
    assert '/documents/contacts/' in rules and '/documents/privacy/' in rules
    assert 'ЮKassa' not in rules and 'через 14 календарных дней' not in rules
    safety = pages['contraindications']
    assert re.findall(r'<h2>(.*?)</h2>', safety) == [
        '1. Общие противопоказания', '2. Локальные противопоказания',
        '3. Относительные противопоказания', '4. Требования безопасности', '5. Возможные реакции',
    ]
    assert len(re.findall(r'<li>', safety)) == 23
    assert re.findall(r'<p>(4\.\d+)\.', safety) == [f'4.{n}' for n in range(1, 6)]
    assert 'незамедлительно вызвать скорую медицинскую помощь' in safety
    assert '/documents/rules/' in safety
    contacts = pages['contacts']
    assert 'кв. 109.' in contacts and 'кв./офис' not in contacts
    assert 'tel:+79951568066' in contacts and 'mailto:info@denisyuce.com' in contacts
    assert '773123178360' in contacts and 'ЮKassa' not in contacts
    privacy = pages['privacy']
    assert re.findall(r'<h2>(.*?)</h2>', privacy) == [
        '1. Общие положения', '2. Цели, состав и основания обработки персональных данных',
        '3. Порядок обработки и передачи персональных данных',
        '4. Использование файлов cookie и веб-аналитика', '5. Сроки хранения и прекращение обработки',
        '6. Защита персональных данных', '7. Права субъектов персональных данных и заключительные положения',
    ]
    assert len(re.findall(r'<h3>', privacy)) == 6
    for section, count in [(1, 3), (3, 9), (4, 5), (5, 4), (6, 2), (7, 6)]:
        assert re.findall(rf'<p>({section}\.\d+)\.', privacy) == [f'{section}.{n}' for n in range(1, count + 1)]
    assert 'сами по себе не являются предоставлением согласия' in privacy
    assert 'ООО «ЯНДЕКС»' in privacy and '/documents/consent/' in privacy
    consent = pages['consent']
    assert re.findall(r'<h2>(.*?)</h2>', consent) == [
        '1. Цели обработки', '2. Персональные данные', '3. Порядок обработки',
        '4. Срок действия и отзыв согласия', '5. Заключительные положения',
    ]
    assert len(re.findall(r'<li>', consent)) == 10
    assert 'ООО «УАЙКЛАЕНТС»' in consent
    assert 'направление рекламы и веб-аналитику' in consent
    assert '/documents/privacy/' in consent and '/documents/contacts/' in consent
    assert 'Редакция от' not in consent and 'кв./офис' not in consent
    print('Verified 5 legal pages, current rules, safety requirements, contacts and local links')


if __name__ == '__main__':
    main()
