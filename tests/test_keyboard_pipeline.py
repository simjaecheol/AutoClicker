"""
Test script to verify the keyboard recording pipeline works correctly.
Simulates raw keyboard events and validates the full conversion + post-processing pipeline.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.raw_event import RawEvent, EventType
from src.models.action import ActionType
from src.recorder.action_converter import ActionConverter
from src.recorder.post_processor import RecordingPostProcessor
from src.recorder.event_aggregator import AggregatorConfig


def create_key_events(chars: str, base_time: float = 0.0, typing_interval: float = 0.1):
    """Simulate realistic key press/release events for typing a string."""
    events = []
    t = base_time
    for ch in chars:
        events.append(RawEvent(type=EventType.KEY_PRESS, timestamp=t, data={"key": ch}))
        events.append(RawEvent(type=EventType.KEY_RELEASE, timestamp=t + 0.03, data={"key": ch}))
        t += typing_interval
    return events


def test_basic_typing():
    """Test: Typing 'hello' should produce a TEXT_INPUT action."""
    print("=" * 60)
    print("TEST 1: Basic typing 'hello'")
    print("=" * 60)
    
    events = create_key_events("hello")
    
    converter = ActionConverter()
    config = AggregatorConfig()
    actions = converter.convert(events, config)
    
    print(f"  Converter output ({len(actions)} actions):")
    for a in actions:
        print(f"    {a.type.value}: {a.params} delay={a.delay_after:.3f}")
    
    processor = RecordingPostProcessor()
    refined = processor.process(actions)
    
    print(f"  Post-processor output ({len(refined)} actions):")
    for a in refined:
        print(f"    {a.type.value}: {a.params} delay={a.delay_after:.3f}")
    
    # Verify
    assert len(refined) == 1, f"Expected 1 TEXT_INPUT, got {len(refined)}"
    assert refined[0].type == ActionType.TEXT_INPUT, f"Expected TEXT_INPUT, got {refined[0].type}"
    assert refined[0].params["text"] == "hello", f"Expected 'hello', got '{refined[0].params['text']}'"
    print("  ✅ PASS\n")


def test_single_char():
    """Test: Single character should remain as KEY_PRESS."""
    print("=" * 60)
    print("TEST 2: Single character 'a'")
    print("=" * 60)
    
    events = create_key_events("a")
    
    converter = ActionConverter()
    config = AggregatorConfig()
    actions = converter.convert(events, config)
    refined = RecordingPostProcessor().process(actions)
    
    print(f"  Result ({len(refined)} actions):")
    for a in refined:
        print(f"    {a.type.value}: {a.params}")
    
    assert len(refined) == 1
    assert refined[0].type == ActionType.KEY_PRESS
    assert refined[0].params["key"] == "a"
    print("  ✅ PASS\n")


def test_special_keys():
    """Test: Special keys like 'enter' should remain as KEY_PRESS."""
    print("=" * 60)
    print("TEST 3: Special key 'enter'")
    print("=" * 60)
    
    events = [
        RawEvent(type=EventType.KEY_PRESS, timestamp=0.0, data={"key": "enter"}),
        RawEvent(type=EventType.KEY_RELEASE, timestamp=0.03, data={"key": "enter"}),
    ]
    
    converter = ActionConverter()
    config = AggregatorConfig()
    actions = converter.convert(events, config)
    refined = RecordingPostProcessor().process(actions)
    
    print(f"  Result ({len(refined)} actions):")
    for a in refined:
        print(f"    {a.type.value}: {a.params}")
    
    assert len(refined) == 1
    assert refined[0].type == ActionType.KEY_PRESS
    assert refined[0].params["key"] == "enter"
    print("  ✅ PASS\n")


def test_mixed_typing_and_clicks():
    """Test: Click, then type 'abc', then click — all should be present."""
    print("=" * 60)
    print("TEST 4: Mixed click + typing + click")
    print("=" * 60)
    
    events = [
        RawEvent(type=EventType.MOUSE_CLICK, timestamp=0.0, data={"x": 100, "y": 200, "button": "left"}),
        RawEvent(type=EventType.MOUSE_RELEASE, timestamp=0.05, data={"x": 100, "y": 200, "button": "left"}),
        *create_key_events("abc", base_time=0.5),
        RawEvent(type=EventType.MOUSE_CLICK, timestamp=1.5, data={"x": 300, "y": 400, "button": "left"}),
        RawEvent(type=EventType.MOUSE_RELEASE, timestamp=1.55, data={"x": 300, "y": 400, "button": "left"}),
    ]
    
    converter = ActionConverter()
    config = AggregatorConfig()
    actions = converter.convert(events, config)
    refined = RecordingPostProcessor().process(actions)
    
    print(f"  Result ({len(refined)} actions):")
    for a in refined:
        print(f"    {a.type.value}: {a.params}")
    
    assert len(refined) == 3, f"Expected 3 actions (click, text, click), got {len(refined)}"
    assert refined[0].type == ActionType.LEFT_CLICK
    assert refined[1].type == ActionType.TEXT_INPUT
    assert refined[1].params["text"] == "abc"
    assert refined[2].type == ActionType.LEFT_CLICK
    print("  ✅ PASS\n")


def test_no_key_release_in_output():
    """Test: No KEY_RELEASE actions should appear in the output."""
    print("=" * 60)
    print("TEST 5: No KEY_RELEASE in output")
    print("=" * 60)
    
    events = create_key_events("test", typing_interval=0.08)
    
    converter = ActionConverter()
    config = AggregatorConfig()
    actions = converter.convert(events, config)
    
    key_releases = [a for a in actions if a.type == ActionType.KEY_RELEASE]
    print(f"  Converter output: {len(actions)} actions, {len(key_releases)} KEY_RELEASE")
    
    assert len(key_releases) == 0, f"Found {len(key_releases)} KEY_RELEASE actions in converter output!"
    print("  ✅ PASS\n")


def test_delay_preservation():
    """Test: Typing delays should reflect actual typing rhythm, not key press-release gap."""
    print("=" * 60)
    print("TEST 6: Delay preserves typing rhythm")
    print("=" * 60)
    
    events = [
        RawEvent(type=EventType.KEY_PRESS, timestamp=0.0, data={"key": "a"}),
        RawEvent(type=EventType.KEY_RELEASE, timestamp=0.03, data={"key": "a"}),
        RawEvent(type=EventType.KEY_PRESS, timestamp=0.2, data={"key": "b"}),
        RawEvent(type=EventType.KEY_RELEASE, timestamp=0.23, data={"key": "b"}),
    ]
    
    converter = ActionConverter()
    config = AggregatorConfig()
    actions = converter.convert(events, config)
    
    print(f"  KEY_PRESS 'a' delay_after = {actions[0].delay_after:.3f}s (expect ~0.2)")
    
    # delay should be ~0.2 (time to next KEY_PRESS), NOT ~0.03 (time to KEY_RELEASE)
    assert actions[0].delay_after > 0.15, f"Delay too short: {actions[0].delay_after}"
    print("  ✅ PASS\n")


if __name__ == "__main__":
    test_basic_typing()
    test_single_char()
    test_special_keys()
    test_mixed_typing_and_clicks()
    test_no_key_release_in_output()
    test_delay_preservation()
    
    print("=" * 60)
    print("🎉 ALL TESTS PASSED")
    print("=" * 60)
