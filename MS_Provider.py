import copy
import math
import random
import time

import Agent
import utils
from ArrivalNode import ArrivalNode
from Message import Message, MsgUtilityOffer, MsgBeliefVector, MsgInitFromRequster, MsgProviderChoice
from Provider import Provider

class MS_Provider(Provider):
    def __init__(self, id_, problem_id, skill_set, travel_speed=5):
        super().__init__(id_, problem_id, skill_set, travel_speed)
        self.Belief = {}
        self.med_Belief = {}
        self.incoming_utility_messages = []
        self.mistake_probability = 0.1
        self.possible_arrival_times = []

        self.After_fmr = 0
        self.cur_iter_fmr = False

    def up_fmr(self):
        if not self.cur_iter_fmr:
            self.After_fmr += 1
            self.cur_iter_fmr = True

    def full_reset(self):
        super().full_reset()
        self.Belief = {}
        self.incoming_utility_messages = []
        self.mistake_probability = 0.1
        self.cur_iter_fmr = False
        self.set_up_possible_arrival_times()
        for key in self.neighbor_util.keys():
            self.Belief[key] = ArrivalNode(0,0)


    def open_mail(self):
        for massage in self.inmessagebox:
            if isinstance(massage,MsgUtilityOffer):
                self.incoming_utility_messages.append(massage)
            if isinstance(massage, MsgInitFromRequster):
                self.incoming_setupmessages.append(massage)
            # add other messages handling here
        self.inmessagebox.clear()

    def initate(self):
      pass

    def compute(self):
        self.open_mail()
        self.update_belief()
        self.avg_belief()
        self.normalize_belief_vector()
        #self.act_human()
        self.make_a_choice()
        self.generate_result_messages()

    def send_belief_msg(self, requester_id: int) -> None:
        msg = MsgBeliefVector(self.id_,requester_id,self.med_Belief)
        self.outmessagebox.append(msg)

    def generate_result_messages(self):
        for neighbour in self.neighbor_data.keys():
            self.send_belief_msg(neighbour)

    def reset_belief(self):
        #self.Belief.clear()
        for key in self.neighbor_util.keys():
            self.Belief[key] = ArrivalNode(0,0)
            if self.possible_arrival_times != []:
                for path in self.possible_arrival_times:
                    self.Belief[path[0][0]].insert_path(path)

        self.possible_arrival_times = []


    def update_belief(self):
        # damping
        for key in self.Belief.keys():
            self.Belief[key].damping()

        #update
        res = {}
        for offer_dict in self.incoming_utility_messages:
            for key,value in offer_dict.context.items():
                if key not in res:
                    res[key] = [0,0]
                res[key][0] += value[0]
                res[key][1] += value[1]
        if res != {}:
            for key in self.Belief.keys():
                self.Belief[key].update_nodes_util(res)
        self.incoming_utility_messages.clear()



    def avg_belief(self):
        for key in self.med_Belief.keys():
            self.med_Belief[key] = 0

        for perm in self.Belief.keys():
            self.med_Belief[self.Belief[perm].id] = 0
            for key in self.Belief.keys():
                self.med_Belief[self.Belief[perm].id] += self.Belief[key].get_id_total_util(perm)


    def act_human(self):
        '''
       Novelty
       '''

        if random.random() > 1 - self.mistake_probability:
            res = {}
            for key in self.Belief.keys():
                res[key] = [0,0]
            for key in self.Belief.keys():
                self.Belief[key].update_nodes_util(res)


    def normalize_belief_vector(self):
        if not self.med_Belief:
            return
        min_value = 100000
        for value in self.med_Belief.values():
            if value < min_value and value != 0:
                min_value = value
        for key in self.med_Belief.keys():
            if self.med_Belief[key] >= min_value:
                self.med_Belief[key] -= min_value
        for key in self.Belief.keys():
             self.med_Belief[key] *= 0.001

    def make_a_choice(self):
        best_choice = 0
        for key in self.Belief.keys():
            temp_path = [(self.Belief[key].id,self.Belief[key].arrival_time,self.Belief[key].util)]
            self.Belief[key].find_max_path(temp_path)
            local_sum = 0
            for i in temp_path:
                local_sum+=i[2]
            if local_sum >= best_choice:
                best_choice = local_sum
                self.chosen_requesters = [temp_path[0]]

        if self.chosen_requesters != []:
            for elem in self.chosen_requesters:
                Choice = MsgProviderChoice(self.id_,elem[0],elem)
                self.outmessagebox.append(Choice)
                break



    def remove_neighbour(self, agent) -> None:
        super().remove_neighbour(agent)
        if type(agent) == int:
            del self.Belief[agent]
        else:
            del self.Belief[agent.id_]
        messages_to_remove = []
        for message in self.outmessagebox:
            if message.receiver_id not in self.neighbor_data.keys():
                messages_to_remove.append(message)
        for i in messages_to_remove:
            self.outmessagebox.remove(i)
        messages_to_remove.clear()
        for id in self.message_data:
            if id not in self.neighbor_data:
                messages_to_remove.append(id)
        for i in messages_to_remove:
            del self.message_data[i]



    def set_up_possible_arrival_times(self):
        possible_times = []
        conkeys = list(self.connections.keys())
        for key in conkeys:
            newconkey = copy.deepcopy(conkeys)
            newconkey.remove(key)
            if newconkey == []:
                possible_times.append([key])
                break
            tempres = []
            utils.heapPermutation(newconkey,len(newconkey),tempres)
            for i in tempres:
                i.insert(0,key)
            possible_times.extend(tempres)
        ord_num = 0
        for order in possible_times:
            self.possible_arrival_times.append([])
            place_in_order = 0
            for id in order:
                if place_in_order == 0:
                    self.possible_arrival_times[ord_num].append((id,utils.Calculate_Distance(self.current_location, self.connections[id])/self.travel_speed))
                else:
                    self.possible_arrival_times[ord_num].append((id, self.requester_service_times[order[place_in_order-1]]+self.possible_arrival_times[ord_num][len(self.possible_arrival_times[ord_num])-1][1]+(utils.Calculate_Distance(self.connections[order[place_in_order-1]],self.connections[id])/self.travel_speed)))
                place_in_order+=1
            ord_num +=1




    def Decay_Function(self,requester_id,Util_Decay_Func):
        res = []

        for line in self.possible_arrival_times:
            for elem in line:
                if elem[0] == requester_id:
                    res.append((elem[1],Util_Decay_Func(elem[1])))

        return res
