// Single source of truth for provider choices + suggested models. Mirrors the
// detection logic in apps/ai-review-service/app/llm.py (detect_provider) so the
// UI can auto-detect a provider the instant a key is pasted, without a round trip.

export type ProviderId = 'auto' | 'openai' | 'azure_openai' | 'anthropic' | 'gemini' | 'openai_compatible';

export type ProviderOption = {
  id: ProviderId;
  label: string;
  models: string[];
  requiresEndpoint?: boolean;
};

export const PROVIDERS: ProviderOption[] = [
  { id: 'auto', label: 'Auto detect', models: [] },
  {
    id: 'openai',
    label: 'OpenAI',
    models: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo']
  },
  {
    id: 'azure_openai',
    label: 'Azure OpenAI',
    models: ['gpt-4o', 'gpt-4o-mini', 'gpt-35-turbo'],
    requiresEndpoint: true
  },
  {
    id: 'anthropic',
    label: 'Anthropic (Claude)',
    models: ['claude-opus-4-8', 'claude-sonnet-4-6', 'claude-haiku-4-5-20251001', 'claude-fable-5']
  },
  {
    id: 'gemini',
    label: 'Google Gemini',
    // Per https://ai.google.dev/gemini-api/docs/models (current as of this writing).
    // gemini-2.5-flash is the recommended stable default; older 1.5/2.0 models remain
    // selectable for accounts still on them. Free-tier access is per-project, not per
    // model, so a quota error here means the Google Cloud project needs free-tier/billing
    // enabled at https://aistudio.google.com/apikey, not a different model choice.
    models: ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.5-flash-lite', 'gemini-2.0-flash']
  },
  {
    id: 'openai_compatible',
    label: 'OpenAI-compatible (custom endpoint)',
    models: [],
    requiresEndpoint: true
  }
];

export function findProvider(id: string): ProviderOption | undefined {
  return PROVIDERS.find((provider) => provider.id === id);
}

/** Mirrors backend detect_provider() in app/llm.py and app/provider_detect.py. */
export function detectProvider(apiKey: string, endpoint?: string, model?: string): ProviderId {
  const endpointLower = (endpoint ?? '').toLowerCase();
  const modelLower = (model ?? '').toLowerCase();
  if (endpointLower.includes('openai.azure.com')) return 'azure_openai';
  if (apiKey.startsWith('sk-ant-')) return 'anthropic';
  if (endpointLower.includes('generativelanguage.googleapis.com') || modelLower.includes('gemini')) return 'gemini';
  if (apiKey.startsWith('AIza')) return 'gemini';
  if (apiKey.startsWith('sk-')) return 'openai';
  if (endpoint) return 'openai_compatible';
  return 'auto';
}
