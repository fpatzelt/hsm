from __future__ import print_function

import threading
import time

from hsm.core import State, Container, StateMachine, Event
from hsm.introspection import IntrospectionServer
import hsm.ros  # augments hsm.core.State with ros_subscribe()

import logging
logging.getLogger('pysm').setLevel(logging.INFO)

import rospy
from std_msgs.msg import String

# It's possible to encapsulate all state related behaviour in a state class.
class HeatingState(Container):
    def __init__(self, name):
        super(HeatingState, self).__init__(name)
        baking = State('Baking')
        self.add_state(baking, initial=True)
        toasting = State('Toasting')
        self.add_state(toasting)

    def on_enter(self, event):
        oven = event.userdata['source_event'].userdata['oven']
        if not oven.timer.is_alive():
            oven.start_timer()
        print('Heating on')

    def on_exit(self, event):
        print('Heating off')


class Oven(object):
    TIMEOUT = 6

    def __init__(self):
        self.sm = self._get_state_machine()
        self.timer = threading.Timer(Oven.TIMEOUT, self.on_timeout)

    def _get_state_machine(self):
        oven = StateMachine('Oven')

        door_closed = Container('Door closed')
        oven.add_state(door_closed, initial=True)
        off = door_closed.add_state('Off', initial=True)
        heating = door_closed.add_state(HeatingState('Heating'))

        door_open = oven.add_state('Door open')

        oven.add_transition(door_closed, heating['Toasting'], events=['toast'])
        oven.add_transition(door_closed, heating['Baking'], events=['bake'])
        oven.add_transition(door_closed, off, events=['off', 'timeout'])
        oven.add_transition(door_closed, door_open, events=['open'])

        # define enter/exit/event handlers as arbitrary callbacks
        door_open.add_handler('enter', self.on_open_enter)
        door_open.add_handler('exit', self.on_open_exit)
        door_open.add_handler('close', self.on_door_close)

        oven.ros_subscribe("chatter", String, self.handler)
        oven.initialize()
        return oven

    def handler(self, msg):
        print(msg)

    @property
    def state(self):
        return self.sm.leaf_state.name

    def light_on(self):
        print('Light on')

    def light_off(self):
        print('Light off')

    def start_timer(self):
        self.timer.start()

    def bake(self):
        self.sm.dispatch(Event('bake', oven=self))

    def toast(self):
        self.sm.dispatch(Event('toast', oven=self))

    def open_door(self):
        self.sm.dispatch(Event('open', oven=self))

    def close_door(self):
        self.sm.dispatch(Event('close', oven=self))

    def on_timeout(self):
        print('Timeout...')
        self.sm.dispatch(Event('timeout', oven=self))
        self.timer = threading.Timer(Oven.TIMEOUT, self.on_timeout)

    def on_open_enter(self, state, event):
        print('Opening door')
        self.light_on()

    def on_open_exit(self, state, event):
        print('Closing door')
        self.light_off()

    def on_door_close(self, state, event):
        # Transition to a history state
        self.sm.set_previous_leaf_state(event)


def test_oven():
    oven = Oven()
    sis = IntrospectionServer('hsm_introspection', oven.sm, 'Oven')
    sis_thread = threading.Thread(target=sis.start)
    sis_thread.start()

    print(oven.state)
    assert oven.state == 'Off'
    time.sleep(5)
    oven.bake()
    print(oven.state)
    assert oven.state == 'Baking'

    time.sleep(5)

    oven.open_door()
    print(oven.state)
    assert oven.state == 'Door open'

    time.sleep(5)
    oven.close_door()
    print(oven.state)
    assert oven.state == 'Baking'

    time.sleep(7)

    print(oven.state)
    assert oven.state == 'Off'

    time.sleep(5)
    sis.stop()

if __name__ == '__main__':
    rospy.init_node('oven')
    test_oven()
