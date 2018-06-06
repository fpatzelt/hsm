from __future__ import print_function

from hsm.core import StateMachine, CallbackState
import time


class Compute(StateMachine):
    TIMEOUT = 1

    def __init__(self):
        super(Compute, self).__init__("root")
        self.done_count = 0

        compute = self.add_state(CallbackState("compute", self.compute))
        idle = self.add_state("idle", initial=True)
        done = self.add_state("done")
        done.add_handler("enter", self.count)

        # switch between states
        self.add_transition(compute, idle, "switch")
        self.add_transition(idle, compute, "switch")
        self.add_transition(compute, done, "done")

    def compute(self, event):
        for i in range(5):
            time.sleep(0.1)
            print(i)
        print("ready")
        return "done"

    def count(self, state, event):
        self.done_count += 1

    def on_transition(self):
        print(self.leaf_state.name)


if __name__ == '__main__':
    sm = Compute()
    sm.register_transition_cb(sm.on_transition)
    sm.initialize()
    assert(sm.leaf_state.name == "idle")

    sm.dispatch("switch")
    assert(sm.leaf_state.name == "compute")
    time.sleep(0.3)

    sm.dispatch("switch")
    assert(sm.leaf_state.name == "idle")
    assert(sm.done_count == 0)

    sm.dispatch("switch")
    assert(sm.leaf_state.name == "compute")

    time.sleep(1.0)
    assert(sm.leaf_state.name == "done")
    assert(sm.done_count == 1)
