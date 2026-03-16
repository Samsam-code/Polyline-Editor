from .toolbar import Toolbar
from .selection_manager import SelectionManager

ADD_POINT = "Add Point"
MOVE_SPLIT = "Move / Split"
DELETE_POINT = "Delete Point"
FLIP = "Flip"
CLEAR = "Clear"
EXPORT_TIKZ = "Export TikZ"

class UIManager:
    def __init__(self):
        self.toolbar = Toolbar([
            ADD_POINT,
            MOVE_SPLIT,
            DELETE_POINT,
            FLIP,
            CLEAR,
            EXPORT_TIKZ,
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
