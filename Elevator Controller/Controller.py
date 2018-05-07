from Elevator import Elevator

import threading
import time


class Controller:
    """control a group of elevators"""

    def __init__(self, num_floors, num_elevators):
        self.floors = num_floors
        self.num_elevators = num_elevators
        self.elevators = []
        self.pending_targets = {}
        self.new_floor_calls = []
        self.new_elevator_calls = []
        for i in range(num_elevators):
            self.elevators.append(Elevator(i, self.floors))
            self.pending_targets[i] = []
        self.control_loop = threading.Thread(target=self.state_loop, args=(True,))
        self.control_loop.start()
        self.input_loop()

    def state_loop(self, debug=False):
        """state machine event-based elevator algorithm"""
        while True:
            new_reqs = []
            if len(self.new_floor_calls) > 0:
                for floor in self.new_floor_calls:
                    new_reqs.append(floor)
                    self.elevators[0].target(int(new_reqs[0]))
            # if len(self.new_elevator_calls) > 0:
            #     for arr in self.new_elevator_calls:
            #         new_reqs.append(arr)
            self.update_routine()
            time.sleep(1)

    def input_loop(self):
        while True:
            data1 = input(
                "\nPress 'c' to make a new elevator call.\nPress 'd' to direct an elevator.\nPress 'p' to print out elevators. \n")
            if data1 == "c":
                data2 = input("Choose a floor (1-" + str(self.floors - 1) + ")")
                self.new_floor_calls.append(data2)
            elif data1 == "d":
                data2 = input("Choose your elevator: 0-" + str(self.num_elevators - 1))
                data3 = input("Now choose a floor (0-" + str(self.floors - 1) + ")")
                self.new_elevator_calls.append([data2, data3])
            elif data1 == "p":
                for elevator in self.elevators:
                    print(elevator)

    def update_routine(self):
        for elevator in self.elevators:
            elevator.update()


if __name__ == "__main__":
    controller1 = Controller(10, 1)
