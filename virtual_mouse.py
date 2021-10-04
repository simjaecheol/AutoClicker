from pynput.mouse import Button, Controller

class VirtualMouse:
    def __init__(self):
        self.mouse = Controller()

    def get_position(self):
        return self.mouse.position

    def set_position(self, x_pos, y_pos):
        self.mouse.position = (x_pos, y_pos)

    def move(self, x_pos, y_pos):
        self.mouse.move(x_pos, y_pos)
    
    def click(self):
        self.mouse.click(Button.left)
    
    def double_click(self):
        self.mouse.click(Button.left, 2)
    
    def right_click(self):
        self.mouse.click(Button.right)
    
    def drag(self, from_x, from_y, to_x, to_y):
        self.mouse.move(from_x, from_y)
        self.mouse.press(Button.left)
        self.mouse.move(to_x, to_y)
        self.mouse.release(Button.left)
