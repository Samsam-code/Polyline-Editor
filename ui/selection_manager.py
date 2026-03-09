class SelectionManager:
    def __init__(self):
        # single selection
        self.selected_point = None

        # hover
        self.hover_point = None
        self.hover_edge_index = None

        # flip 
        self.flip_base_index = None
        self.flip_candidates = [] # list of (flip_type, (p1, p2))

    def clear(self):
        self.selected_point = None

    def clear_hover(self):
        self.hover_point = None
        self.hover_edge_index = None

    def clear_flip(self):
        self.flip_base_index = None
        self.flip_candidates = []

    def select_point(self, point):
        self.selected_point = point
