import copy
import math

from Message import Message, MsgInitFromProvider

from Agent import Agent
from utils import Calculate_Distance


class Provider(Agent):
    def __init__(self, id_, problem_id, skill_set, travel_speed=5):
        Agent.__init__(self, id_, problem_id)
        # Provider Variables
        self.skill_set = skill_set
        self.travel_speed = travel_speed

        self.requester_service_times = {}

        self.incoming_setupmessages = []

        # Algorithm Results
        self.chosen_requesters = []

    def full_reset(self):
        super().full_reset()
        # Algorithm results
        self.chosen_requesters = []

    def __str__(self):
        return "Provider " + Agent.__str__(self)

    def send_init_msg(self, agent_id : int):
        msg_init = MsgInitFromProvider(sender_id=self.id_,
                                       context=[copy.deepcopy(self.current_location),copy.deepcopy(self.skill_set),copy.deepcopy(self.travel_speed),copy.deepcopy(list(self.neighbor_data.keys()))],
                                       receiver_id=agent_id)
        self.outmessagebox.append(msg_init)

    def init_relationships(self):
        for message in self.incoming_setupmessages:
            #self.neighbor_data[message.sender_id] = message.context
            self.requester_service_times[message.sender_id] = message.context

    # def remove_neighbour(self, agent) -> None:
    #     super().remove_neighbour(agent)
    #     if type(agent) == int:
    #         if agent in self.neighbor_data:
    #             del self.neighbor_data[agent]
    #     else:
    #         if agent.id_ in self.neighbor_data:
    #             del self.neighbor_data[agent.id_]

    def make_a_choice(self):
        raise NotImplementedError()
