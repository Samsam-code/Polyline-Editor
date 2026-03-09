from .toolbar import Toolbar
from .selection_manager import SelectionManager

class UIManager:
    def __init__(self):
        self.toolbar = Toolbar([
            "Add Point",
            "Move / Split",
            "Delete Point",
            "Flip",
            "Clear",
            "Export TikZ",
        ])
        self.selection = SelectionManager()

    @property
    def current_mode(self):
        return self.toolbar.current_mode

    def set_mode(self, mode):
        self.toolbar.current_mode = mode

    def draw(self, surface):
        self.toolbar.draw(surface)

    def handle_click(self, pos):
        return self.toolbar.handle_click(pos)
