from dataclasses import dataclass

@dataclass
class AggregatorConfig:
    double_click_threshold: float = 0.3    # seconds
    drag_distance_threshold: int = 5       # pixels
    text_merge_threshold: float = 0.5      # seconds
    ignore_window_title: str = "AutoClicker"  # UI window title to ignore
    record_mouse_move: bool = False        # whether to record simple mouse moves
    min_delay_threshold: float = 0.05      # delays shorter than this are treated as 0
    max_delay_cap: float = 30.0            # cap maximum delay to avoid long pauses
