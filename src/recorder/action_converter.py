import math
from typing import List
from models.action import Action, ActionType
from models.raw_event import RawEvent, EventType
from recorder.event_aggregator import AggregatorConfig

class ActionConverter:
    def convert(self, events: List[RawEvent], config: AggregatorConfig) -> List[Action]:
        if not events:
            return []
            
        actions: List[Action] = []
        i = 0
        n = len(events)
        
        while i < n:
            event = events[i]
            
            # calculate delay to next event
            delay = 0.0
            if i + 1 < n:
                delay = events[i+1].timestamp - event.timestamp
                
                # Apply delay threshold and cap
                if delay < config.min_delay_threshold:
                    delay = 0.0
                elif delay > config.max_delay_cap:
                    delay = config.max_delay_cap
            
            # --- MOUSE EVENTS ---
            if event.type == EventType.MOUSE_CLICK:
                # Look ahead for a matching RELEASE
                release_idx = self._find_next(events, i + 1, EventType.MOUSE_RELEASE)
                if release_idx != -1 and release_idx <= i + 5: # Limit lookahead
                    release_ev = events[release_idx]
                    
                    # Calculate delay from the RELEASE event to the next event
                    release_delay = 0.0
                    if release_idx + 1 < n:
                        release_delay = events[release_idx + 1].timestamp - release_ev.timestamp
                        if release_delay < config.min_delay_threshold:
                            release_delay = 0.0
                        elif release_delay > config.max_delay_cap:
                            release_delay = config.max_delay_cap
                    
                    # Check if it was a drag (significant coordinate change)
                    dist = math.hypot(release_ev.data["x"] - event.data["x"], release_ev.data["y"] - event.data["y"])
                    if dist > config.drag_distance_threshold:
                        actions.append(Action(
                            type=ActionType.DRAG,
                            params={
                                "from_x": event.data["x"], "from_y": event.data["y"],
                                "to_x": release_ev.data["x"], "to_y": release_ev.data["y"]
                            },
                            delay_after=release_delay,
                            description=f"Drag from {event.data['x']},{event.data['y']} to {release_ev.data['x']},{release_ev.data['y']}"
                        ))
                    else:
                        # It's a click
                        action_type = ActionType.LEFT_CLICK if event.data.get("button") == "left" else ActionType.RIGHT_CLICK
                        actions.append(Action(
                            type=action_type,
                            params={"x": event.data["x"], "y": event.data["y"]},
                            delay_after=release_delay,
                            description=f"{action_type.name} at {event.data['x']},{event.data['y']}"
                        ))
                    
                    # Skip processed events
                    i = release_idx
                else:
                    # No release found nearby, just record the press if needed (or ignore)
                    pass
                    
            elif event.type == EventType.MOUSE_SCROLL:
                amount = event.data.get("dy", 0)
                if amount != 0:
                    action_type = ActionType.SCROLL_UP if amount > 0 else ActionType.SCROLL_DOWN
                    actions.append(Action(
                        type=action_type,
                        params={"amount": abs(amount * 100)}, # Arbitrary multiplier for scroll amount
                        delay_after=delay,
                        description=f"Scroll {'Up' if amount > 0 else 'Down'}"
                    ))
                    
            # --- KEYBOARD EVENTS ---
            elif event.type == EventType.KEY_PRESS:
                # Calculate delay to the next meaningful event (skip over KEY_RELEASE)
                # This preserves actual typing rhythm instead of using the tiny
                # KEY_PRESS→KEY_RELEASE gap (~20-50ms)
                key_delay = 0.0
                for k in range(i + 1, n):
                    if events[k].type != EventType.KEY_RELEASE:
                        key_delay = events[k].timestamp - event.timestamp
                        break
                
                if key_delay < config.min_delay_threshold:
                    key_delay = 0.0
                elif key_delay > config.max_delay_cap:
                    key_delay = config.max_delay_cap
                
                actions.append(Action(
                    type=ActionType.KEY_PRESS,
                    params={"key": event.data["key"]},
                    delay_after=key_delay,
                    description=f"Press {event.data['key']}"
                ))
            elif event.type == EventType.KEY_RELEASE:
                # Skip — KEY_PRESS already captures the full key action.
                # Playback uses tap (press+release) for individual keys,
                # or type_text() for merged TEXT_INPUT.
                pass
            
            i += 1
            
        return actions

    def _find_next(self, events: List[RawEvent], start_idx: int, target_type: EventType) -> int:
        for i in range(start_idx, len(events)):
            if events[i].type == target_type:
                return i
        return -1
