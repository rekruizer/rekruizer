import { readFileSync, readdirSync } from "node:fs";
import { join, relative, resolve, sep } from "node:path";

export type LegacySegment =
  | { type: "html"; html: string }
  | { type: "header" }
  | { type: "footer" };

export type LegacyPage = {
  route: string;
  sourcePath: string;
  headHtml: string;
  bodyClass: string;
  segments: LegacySegment[];
};

const ROOT = resolve(process.cwd());
const LEGACY_ROOTS = ["documents", "muscles", "notes", "quizzes", "reviews", "url"];

function indexFiles(directory: string): string[] {
  const result: string[] = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) result.push(...indexFiles(path));
    else if (entry.isFile() && entry.name === "index.html") result.push(path);
  }
  return result;
}

function splitBody(body: string): LegacySegment[] {
  const marker = /<div\s+data-site-(header|footer)(?:="")?\s*><\/div>/gi;
  const segments: LegacySegment[] = [];
  let cursor = 0;
  for (const match of body.matchAll(marker)) {
    const index = match.index ?? 0;
    if (index > cursor) segments.push({ type: "html", html: body.slice(cursor, index) });
    segments.push({ type: match[1].toLowerCase() as "header" | "footer" });
    cursor = index + match[0].length;
  }
  if (cursor < body.length) segments.push({ type: "html", html: body.slice(cursor) });
  return segments.length ? segments : [{ type: "html", html: body }];
}

export function parseLegacyDocument(sourcePath: string, route: string): LegacyPage {
  const source = readFileSync(sourcePath, "utf8");
  const head = source.match(/<head[^>]*>([\s\S]*?)<\/head>/i);
  const body = source.match(/<body([^>]*)>([\s\S]*?)<\/body>/i);
  if (!head || !body) throw new Error(`Invalid legacy HTML: ${relative(ROOT, sourcePath)}`);
  const bodyClass = body[1].match(/class=["']([^"']*)["']/i)?.[1] ?? "";
  return {
    route,
    sourcePath,
    headHtml: head[1],
    bodyClass,
    segments: splitBody(body[2]),
  };
}

export function legacyPages(): LegacyPage[] {
  return LEGACY_ROOTS.flatMap((directory) => indexFiles(join(ROOT, directory)))
    .map((sourcePath) => {
      const relativePath = relative(ROOT, sourcePath).split(sep).join("/");
      return parseLegacyDocument(sourcePath, relativePath.replace(/\/index\.html$/, ""));
    })
    .sort((left, right) => left.route.localeCompare(right.route, "en"));
}

export function legacy404(): LegacyPage {
  return parseLegacyDocument(join(ROOT, "404.html"), "404");
}
