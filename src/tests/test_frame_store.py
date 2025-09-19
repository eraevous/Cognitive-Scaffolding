import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from core.memory import FrameStore


def test_save_and_load(tmp_path):
    store = FrameStore(path=tmp_path)
    store.save_frame("f1", "hello")
    assert store.load_frame("f1") == "hello"


def test_inject_memory(tmp_path):
    store = FrameStore(path=tmp_path)
    store.save_frame("f1", "hello")
    store.save_frame("f2", "foo")
    result = store.inject_memory("world", ["f1", "f2"])
    assert result == "hello\nfoo\nworld"


def test_inject_memory_load_once(tmp_path, monkeypatch):
    store = FrameStore(path=tmp_path)
    store.save_frame("f1", "hello")
    store.save_frame("f2", "foo")

    calls = []

    original = store.load_frame

    def spy(frame_id: str):
        calls.append(frame_id)
        return original(frame_id)

    monkeypatch.setattr(store, "load_frame", spy)
    result = store.inject_memory("world", ["f1", "f2"])
    assert result == "hello\nfoo\nworld"
    assert calls == ["f1", "f2"]
