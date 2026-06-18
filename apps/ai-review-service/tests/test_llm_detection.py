from app.llm import detect_provider


def test_detects_azure_openai() -> None:
    assert detect_provider("abc", "https://demo.openai.azure.com", "gpt-4o") == "azure_openai"


def test_detects_anthropic() -> None:
    assert detect_provider("sk-ant-demo") == "anthropic"


def test_detects_openai_compatible_endpoint() -> None:
    assert detect_provider("abc", "https://llm.example.com") == "openai_compatible"


def test_detects_gemini_by_key_prefix() -> None:
    assert detect_provider("AIzaSyDemoKey") == "gemini"


def test_detects_gemini_by_model_name() -> None:
    assert detect_provider("abc", model="gemini-2.0-flash") == "gemini"
