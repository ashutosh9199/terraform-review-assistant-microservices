from app.services.provider_detect import detect_provider


def test_detects_azure_openai() -> None:
    assert detect_provider("abc", "https://demo.openai.azure.com", "gpt-4o") == "azure_openai"


def test_detects_anthropic() -> None:
    assert detect_provider("sk-ant-demo") == "anthropic"


def test_detects_openai_when_key_looks_like_openai() -> None:
    assert detect_provider("sk-demo") == "openai"


def test_unknown_without_endpoint_or_key_hint() -> None:
    assert detect_provider("randomtoken") == "unknown"
