import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { education } from "../src/data/education.ts";

test("education uses explicit, unique records rather than inferred credentials", () => {
  const ids = new Set();
  for (const entry of education) {
    assert.match(entry.id, /^[a-z][a-z0-9-]*$/);
    assert.ok(!ids.has(entry.id), `Duplicate education record: ${entry.id}`);
    ids.add(entry.id);
    assert.ok(entry.school.trim());
    assert.ok(Number.isInteger(entry.year) && entry.year >= 1900 && entry.year <= new Date().getFullYear());
    assert.ok(typeof entry.programme === "string" && entry.programme.trim());
  }
});

test("the home page never shows an empty education section or a dead anchor", () => {
  const html = readFileSync(new URL("../dist/index.html", import.meta.url), "utf8");
  assert.equal(html.includes('id="education"'), education.length > 0);
  assert.equal(html.includes('href="#education"'), false);
  assert.equal((html.match(/<li\b[^>]*class="education-record"/g) || []).length, education.length);
  for (const entry of education) assert.ok(html.includes(`id="education-${entry.id}"`));
  const schools = [...html.matchAll(/<p\b[^>]*class="education-school"[^>]*>(.*?)<\/p>/gs)];
  assert.equal(schools.length, education.length);
  for (const [, school] of schools) assert.doesNotMatch(school, /[А-ЯЁ]\. (?=[А-ЯЁ])/);
});

test("MCPO training does not replace the separate medical massage qualification", () => {
  assert.equal(education.find((entry) => entry.id === "classic-mcpo")?.year, 2025);
  assert.equal(education.find((entry) => entry.id === "medical-massage")?.programme, "Оздоровительный медицинский массаж");
});
