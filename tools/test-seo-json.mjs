import test from "node:test";
import assert from "node:assert/strict";
import { jsonLd } from "../src/lib/seo.ts";

test("JSON-LD cannot prematurely close its script element; its data stays unchanged", () => {
  const schema = { "@type": "Service", name: 'Массаж </script><script>alert(1)</script>',
    description: '<!-- & " \n \\ 🙂', price: 0 };
  const encoded = jsonLd(schema);
  assert.ok(!encoded.includes("<"));
  assert.deepEqual(JSON.parse(encoded), schema);
});

test("breadcrumbs and schema arrays retain exact URLs and positions", () => {
  const schema = [{ "@type": "BreadcrumbList", itemListElement: [
    { "@type": "ListItem", position: 1, item: "https://denisyuce.com/" },
    { "@type": "ListItem", position: 2, item: "https://denisyuce.com/services/" },
  ] }];
  assert.deepEqual(JSON.parse(jsonLd(schema)), schema);
});
