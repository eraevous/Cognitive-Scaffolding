import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

from core.memory import FrameStore


def test_save_and_load(tmp_path):
    store = FrameStore(path=tmp_path)
    store.save_frame('f1', 'hello')
    assert store.load_frame('f1') == 'hello'


def test_inject_memory(tmp_path):
    store = FrameStore(path=tmp_path)
    store.save_frame('f1', 'hello')
    result = store.inject_memory('world', ['f1'])
    assert result.startswith('hello') and result.endswith('world')
