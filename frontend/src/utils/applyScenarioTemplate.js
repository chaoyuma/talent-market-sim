function deepMerge(target, source) {
  const output = structuredClone(target);

  for (const key of Object.keys(source)) {
    const sourceValue = source[key];
    const targetValue = output[key];

    if (
      sourceValue &&
      typeof sourceValue === "object" &&
      !Array.isArray(sourceValue) &&
      targetValue &&
      typeof targetValue === "object" &&
      !Array.isArray(targetValue)
    ) {
      output[key] = deepMerge(targetValue, sourceValue);
    } else {
      output[key] = sourceValue;
    }
  }
 
  return output;
}

export function applyScenarioTemplate(currentForm, template) {
  if (!template || !template.overrides) {
    return structuredClone(currentForm);
  }

  return deepMerge(currentForm, template.overrides);
}