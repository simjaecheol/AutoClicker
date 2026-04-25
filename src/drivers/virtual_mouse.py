from pynput.mouse import Button, Controller

class VirtualMouse:
    def __init__(self):
        self.mouse = Controller()

    def get_position(self):
        return self.mouse.position

    def set_position(self, x: int, y: int):
        self.mouse.position = (x, y)

    def move(self, x: int, y: int):
        self.mouse.move(x, y)
    
    def click(self):
        self.mouse.click(Button.left)

    def click_at(self, x: int, y: int):
        self.set_position(x, y)
        self.click()
    
    def double_click(self):
        self.mouse.click(Button.left, 2)

    def double_click_at(self, x: int, y: int):
        self.set_position(x, y)
        self.double_click()
    
    def right_click(self):
        self.mouse.click(Button.right)

    def right_click_at(self, x: int, y: int):
        self.set_position(x, y)
        self.right_click()
    
    def drag(self, from_x: int, from_y: int, to_x: int, to_y: int):
        self.set_position(from_x, from_y)
        self.mouse.press(Button.left)
        self.set_position(to_x, to_y)
        self.mouse.release(Button.left)

    def scroll(self, dx: int, dy: int):
        """
        dx: horizontal scroll amount
        dy: vertical scroll amount (positive for up, negative for down)
        """
        self.mouse.scroll(dx, dy)
