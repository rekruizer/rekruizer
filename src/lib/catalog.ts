import catalogue from "../generated/services.json";

export type Service = (typeof catalogue.services)[number];
export type ServiceGroup = (typeof catalogue.groups)[number];
export type Subscription = (typeof catalogue.subscriptions)[number];

export const servicesCatalogue = catalogue;

export function compactDescription(value: string, maximum = 160): string {
  const text = value.replace(/\s+/g, " ").trim();
  if (text.length <= maximum) return text;
  const prefix = text.slice(0, maximum - 1);
  const breakAt = prefix.lastIndexOf(" ");
  return `${prefix.slice(0, breakAt > 0 ? breakAt : undefined).replace(/[ ,.;:—-]+$/, "")}…`;
}

export function groupBySlug(slug: string): ServiceGroup | undefined {
  return catalogue.groups.find((group) => group.slug === slug);
}
