"""エージェントの配線テスト。

TestModel は実際のLLMを呼ばない偽モデルで、登録されたツールを全部呼んでから
ダミーの回答を返す。APIキーも利用枠も使わずに、
「ツールが登録され、呼ばれ、結果がモデルに戻るか」を確かめられる。
"""

from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel

from app.agent import agent

BASE_TOOLS = {"search_glossary", "get_lecture_summary"}


def _parts(result, kind):
    return [p for m in result.all_messages() for p in m.parts if isinstance(p, kind)]


def test_base_tools_are_registered_and_called():
    model = TestModel()
    with agent.override(model=model):
        result = agent.run_sync("LoRAとは？")

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert BASE_TOOLS <= offered  # 演習でツールを足しても壊れないよう「含む」で判定

    called = {p.tool_name for p in _parts(result, ToolCallPart)}
    assert BASE_TOOLS <= called
    assert len(_parts(result, ToolReturnPart)) == len(_parts(result, ToolCallPart))
    assert result.output


def test_glossary_result_reaches_the_model():
    model = TestModel(call_tools=["search_glossary"])
    with agent.override(model=model):
        result = agent.run_sync("RAGとは？")
    returns = _parts(result, ToolReturnPart)
    assert returns and returns[0].tool_name == "search_glossary"


def test_ask_reports_token_usage(monkeypatch, capsys):
    class DummyUsageMetadata:
        prompt_token_count = 123
        candidates_token_count = 45

    class DummyResponse:
        text = "テスト回答"
        usage_metadata = DummyUsageMetadata()

    class DummyModels:
        def generate_content(self, model, contents):
            assert model == "dummy-model"
            assert contents == "質問"
            return DummyResponse()

    class DummyClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.models = DummyModels()

    monkeypatch.setattr("app.ask.MODEL", "dummy-model")
    monkeypatch.setattr("app.ask.get_api_key", lambda: "dummy-key")
    monkeypatch.setattr("app.ask.genai.Client", DummyClient)

    from app.ask import ask

    text = ask("質問")
    captured = capsys.readouterr()

    assert text == "テスト回答"
    assert "入力トークン数: 123" in captured.out
    assert "出力トークン数: 45" in captured.out
