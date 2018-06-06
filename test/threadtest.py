from __future__ import print_function

import threading
import time

from hsm.core import State, Container, StateMachine, Event, ThreadContainer
from hsm.introspection import IntrospectionServer
import hsm.ros  # augments hsm.core.State with ros_subscribe()

import logging
logging.getLogger('pysm').setLevel(logging.INFO)

import rospy
from std_msgs.msg import String


if __name__ == '__main__':
    rospy.init_node('oven')
    sm = StateMachine('STATEMACHINE')

    def stuff():
        for i in range(10):
            time.sleep(1)
            print(i)
        return '42'

    def r42(state, event):
        print('Received 42')


    threadstate = ThreadContainer('THREADCONTAINER', stuff)
    sm.add_state(threadstate,initial=True)
    sm.add_handler('42', r42)
    off = State('OFF')
    sm.add_state(off)
    sm.add_transition(threadstate, off, events=['off'])
    sm.add_transition(off,threadstate, events=['on'])
    sm.initialize()
    print(sm.state)

    time.sleep(5)
    sm.dispatch(Event('off'))
    sm.dispatch(Event('on'))
    time.sleep(12)


