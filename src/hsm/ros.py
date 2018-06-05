from hsm.core import State
import rospy

import logging
_LOGGER = logging.getLogger("hsm.ros")


class _ROSEvent(object):
    def __init__(self, topic, msg_type, handler):
        self.topic = topic
        self.msg_type = msg_type
        self.handler = handler
        self.subscriber = None

def _subscribe_ros_events(state, event):
    # subscribe events
    for e in state._ros_events:
        _LOGGER.debug("subscribing to %", e.topic)
        e.subscriber = rospy.Subscriber(e.topic, e.msg_type, e.handler)


def _unsubscribe_ros_events(state, event):
    # unsubscribe events
    for e in state._ros_events:
        del e.subscriber
        _LOGGER.debug("unsubscribed from %", e.topic)


def _ros_subscribe(state, topic, msg_type, handler):
    if not hasattr(state, '_ros_events'):
        # define _ros_events attribute
        state._ros_events = []
        # on enter, subscribe to topics
        state.add_handler('enter', _subscribe_ros_events)
        # on exit, unsubscribe
        state.add_handler('exit', _unsubscribe_ros_events)
    state._ros_events.append(_ROSEvent(topic, msg_type, handler))


# augment State class with ros_subscribe method
setattr(State, "ros_subscribe", _ros_subscribe)