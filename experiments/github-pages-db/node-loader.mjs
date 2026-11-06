// Test-only Node loader. Next.js resolves extensionless TS imports and JSON
// imports; Node needs those details made explicit. The source is not rewritten.
export async function resolve(specifier, context, nextResolve) {
  if (specifier.startsWith(".") && !/\.[a-z0-9]+$/i.test(specifier)) {
    specifier += ".ts";
  }
  if (specifier.endsWith(".json")) {
    context = { ...context, importAttributes: { ...context.importAttributes, type: "json" } };
  }
  const resolved = await nextResolve(specifier, context);
  if (specifier.endsWith(".json")) {
    return { ...resolved, importAttributes: { ...resolved.importAttributes, type: "json" } };
  }
  return resolved;
}
