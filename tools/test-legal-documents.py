#!/usr/bin/env python3
"""Check legal page routes and the agreed payment scope without external calls."""
import json
import re
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ('rules', 'privacy', 'contacts', 'consent')


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
        assert '773123178360' in source and 'mailto:info@denisyuce.com' in source, slug
        assert 'Редакция от 06.11.2026.' in source, slug
        assert 'DIKIDI' not in source, slug
        assert not re.search(r'паспорт гражданина|ключ\s*:\s*\d|CLOUDFLARE_API_TOKEN', source, re.I), slug
        if slug == 'consent':
            assert 'href="/documents/consent/"' not in footer
        else:
            assert f'href="/documents/{slug}/"' in footer, slug
        for href in page.links:
            if href.startswith('/documents/'):
                assert (ROOT / href.lstrip('/') / 'index.html').is_file(), (slug, href)
        for schema in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', source, re.S):
            json.loads(schema)
        built = ROOT / 'dist/documents' / slug / 'index.html'
        if built.exists():
            rendered = built.read_text()
            assert '<header class="site-header">' in rendered and '<footer>' in rendered, slug
            assert '773123178360' in rendered and 'info@denisyuce.com' in rendered, slug

    rules = pages['rules']
    assert 'после подтверждения Исполнителем даты и времени' in rules
    assert 'Оплата разовой услуги производится после оказания услуги' in rules
    assert 'не устанавливают обязательную предоплату для всех записей' in rules
    assert 'Частичная оплата и рассрочка настоящими Правилами не предусмотрены' in rules
    assert 'ЮKassa' in rules and 'чек плательщика налога на профессиональный доход' in rules
    assert 'самостоятельно формирует через приложение «Мой налог»' not in rules
    assert 'Настоящие Правила не устанавливают безусловно невозвратную предоплату' in rules
    assert 'до начала его использования' in rules and 'Покупка абонемента не подтверждает конкретную дату' in rules
    assert 'подтверждает приобретение оплаченного объёма услуг' in rules
    assert 'не требует одновременного согласования дат всех сеансов' in rules
    assert 'момент начала этого срока' in rules
    assert 'разделённой на количество сеансов' in rules
    assert 'не гарантирует доступность любой выбранной клиентом даты' in rules
    assert 'при первом фактически оказанном сеансе по этому абонементу' in rules
    assert 'через 14 календарных дней после продажи' in rules
    assert 'не означают оказания неиспользованных сеансов' in rules
    assert 'фактически понесённых' in rules and 'подтверждены' in rules
    assert 'само посещение сайта' in pages['privacy'].lower()
    assert 'не являются предоставлением такого согласия' in pages['privacy']
    assert 'согласие не распространяется на рекламные рассылки' in pages['consent'].lower()
    assert 'в форме записи или приобретения абонемента' in pages['consent']
    assert 'номер, срок действия и сведения об использовании абонемента' in pages['consent']
    assert 'оформление абонементов' in pages['privacy']
    assert 'организация и проведение акций, мероприятий, розыгрышей, программ лояльности' in pages['privacy']
    assert 'направление информационных и рекламных сообщений' in pages['privacy']
    assert 'Яндекс Карты' not in pages['privacy']
    assert 'Состав услуг, количество и продолжительность сеансов' in rules
    assert 'сообщёнными клиенту до оплаты в карточке предложения' in rules
    assert 'не прекращают обязательства по уже оплаченным услугам' in rules
    assert 'не является основанием автоматически списать его полную стоимость' in rules
    assert '/documents/consent/' in pages['privacy'] and '/documents/consent/' in rules
    assert 'Трансграничная передача персональных данных Оператором не осуществляется' not in pages['privacy']
    print('Verified 4 legal pages, local document links and unchanged manual booking/payment scope')


if __name__ == '__main__':
    main()
