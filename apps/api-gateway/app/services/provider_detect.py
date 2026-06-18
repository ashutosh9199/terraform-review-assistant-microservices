def detect_provider(api_key: str, endpoint: str | None = None, model: str | None = None) -> str:
    """Infer the LLM provider from the supplied credentials.

    Kept in the gateway because settings are validated synchronously when an
    admin saves them. The ai-review-service carries its own copy for runtime use.
    """
    endpoint_lower = (endpoint or "").lower()
    model_lower = (model or "").lower()
    if "openai.azure.com" in endpoint_lower:
        return "azure_openai"
    if api_key.startswith("sk-ant-"):
        return "anthropic"
    if "generativelanguage.googleapis.com" in endpoint_lower or "gemini" in model_lower:
        return "gemini"
    if api_key.startswith("sk-"):
        return "openai"
    if endpoint:
        return "openai_compatible"
    return "unknown"
