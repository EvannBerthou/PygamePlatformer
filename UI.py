class UIManager:
    elements = []

    def add(element):
        if element in UIManager.elements:
            raise ValueError(f'{element} is already in the list')

        UIManager.elements.append(element)
        print('New UI Element added')

class UIElement:
    def __init__(self, x,y):
        self.x, self.y = x,y
        UIManager.add(self)

    def draw(self, surface):
        raise NotImplementedError("UI Element draw")

    def update(self):
        raise NotImplementedError("UI Element draw")

