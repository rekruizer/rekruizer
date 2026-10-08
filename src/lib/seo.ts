/** JSON-LD stays JSON, even when an edited title contains an HTML closing tag. */
export function jsonLd(value: unknown): string {
  return JSON.stringify(value).replace(/</g, "\\u003c");
}
