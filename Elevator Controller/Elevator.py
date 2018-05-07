class Elevator:
    """elevator state"""

    def __init__(self, _id, num_floors):
        self.state = {"motion": 0, "current_floor": 0, "target": -1, "is_bottom": False, "is_top": False}
        self._id = _id
        self.top_floor = num_floors - 1

    def __repr__(self) -> str:
        ret = ""
        ret += "Elevator number: " + str(self._id) + "\n"
        ret += "Current floor: " + str(self.state["current_floor"]) + "\n"
        ret += "The elevator is "
        ret += "not moving" if self.state["motion"] == 0 else "moving " + \
               "upward" if self.state["motion"] == 1 else "downward"
        return ret

    def target(self, floor):
        """elevator assigned new target"""
        assert (0 <= floor <= self.top_floor)
        self.state["target"] = floor
        change = floor - self.state["current_floor"]
        self.state["motion"] = 1 if change > 0 else -1 if change < 0 else 0

    def update(self):
        """move elevator"""
        if self.state["motion"] != 0:
            d = self.state["motion"]
            self.state["current_floor"] += d
            if self.state["current_floor"] == self.state["target"]:
                self.state["motion"] = 0
            if self.state["current_floor"] == self.top_floor:
                self.state["is_top"] = True
            elif self.state["current_floor"] == 0:
                self.state["is_bottom"] = True
            else:
                self.state["is_top"] = False
                self.state["is_bottom"] = False
