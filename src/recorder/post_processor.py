from typing import List
from models.action import Action, ActionType

class RecordingPostProcessor:
    def process(self, actions: List[Action]) -> List[Action]:
        """
        Refines the raw Action list:
        1. Merges sequential KEY_PRESS of simple characters into TEXT_INPUT.
        2. Detects DOUBLE_CLICKs.
        3. Cleans up unnecessary zero-delays.
        """
        if not actions:
            return []
            
        processed = self._merge_text_input(actions)
        processed = self._detect_double_clicks(processed)
        return processed

    def _merge_text_input(self, actions: List[Action]) -> List[Action]:
        """Merge sequential single-character KEY_PRESS actions into TEXT_INPUT.
        
        After the ActionConverter fix, only KEY_PRESS actions are present
        (no KEY_RELEASE), so merging logic is straightforward.
        """
        result: List[Action] = []
        i = 0
        n = len(actions)
        
        while i < n:
            action = actions[i]
            
            # Look for sequential KEY_PRESS of single characters (length 1)
            if action.type == ActionType.KEY_PRESS and len(action.params.get("key", "")) == 1:
                text_buffer = [action.params["key"]]
                last_delay = action.delay_after
                j = i + 1
                
                while j < n:
                    next_action = actions[j]
                    
                    # Merge only if: single char KEY_PRESS AND previous delay was short
                    if (next_action.type == ActionType.KEY_PRESS and 
                        len(next_action.params.get("key", "")) == 1 and
                        last_delay < 1.0):
                        text_buffer.append(next_action.params["key"])
                        last_delay = next_action.delay_after
                        j += 1
                    else:
                        break
                
                if len(text_buffer) > 1:
                    # Merged multiple chars → TEXT_INPUT
                    result.append(Action(
                        type=ActionType.TEXT_INPUT,
                        params={"text": "".join(text_buffer)},
                        delay_after=last_delay,
                        description=f"Type '{''.join(text_buffer)}'"
                    ))
                else:
                    # Single char — keep as KEY_PRESS
                    result.append(action)
                
                i = j
            else:
                result.append(action)
                i += 1
        
        return result

    def _detect_double_clicks(self, actions: List[Action]) -> List[Action]:
        result: List[Action] = []
        i = 0
        n = len(actions)
        
        while i < n:
            action = actions[i]
            
            if action.type == ActionType.LEFT_CLICK and i + 1 < n:
                next_action = actions[i+1]
                
                if next_action.type == ActionType.LEFT_CLICK:
                    # Check if coordinates are identical and delay is short
                    if (action.params.get("x") == next_action.params.get("x") and 
                        action.params.get("y") == next_action.params.get("y") and 
                        action.delay_after < 0.4):
                        
                        result.append(Action(
                            type=ActionType.DOUBLE_CLICK,
                            params={"x": action.params["x"], "y": action.params["y"]},
                            delay_after=next_action.delay_after,
                            description=f"Double Click at {action.params['x']},{action.params['y']}"
                        ))
                        i += 2
                        continue
                        
            result.append(action)
            i += 1
            
        return result
