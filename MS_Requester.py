import copy
import random
import string
import time

import utils
from Message import MsgBeliefVector, MsgUtilityOffer, MsgInitFromProvider, MsgProviderChoice
from Requester import Requester
from utils import to_binary_list, prep_permutate


class MS_Requester(Requester):
    def __init__(self, id_, problem_id, skills_needed, max_skill_types,max_required={}, time_per_skill_unit={}, max_util=1000, max_time=10):
        super().__init__( id_, problem_id, skills_needed,max_skill_types, max_required, time_per_skill_unit, max_util, max_time)

        self.offer = {}
        self.util_message_data = {}
        self.relationship_health = {}
        self.mistake_probability = 0.1



    def full_reset(self):
        super().full_reset()
        self.offer = {}
        self.util_message_data = {}
        self.mistake_probability = 0.1

    def reset_offers(self):
        for id in self.neighbor_data.keys():
            self.offer[id] = {}
            self.relationship_health[id] = 1
            for elem in self.neighbor_data[id][3]:
                self.offer[id][elem] = (0,0)

    def assemble_neighbour_assignments(self):
        self.nclo = len(self.neighbor_util) * len(self.neighbor_util)
        output = {}
        for neighbour in self.neighbor_data.keys():
            output[neighbour] = []
            for key in self.neighbor_data[neighbour][3]:
                output[neighbour].append(key)
        return output


    def create_value_table(self,provider : int) -> list:
        assignments = self.assemble_neighbour_assignments()
        table = []
        amount_of_lines = 1
        for neighbour in assignments.keys():
            amount_of_lines = 1#len(assignments[neighbour])
        permutation = utils.truth_table(assignments, amount_of_lines)#prep_permutate(assignments, amount_of_lines)
        for key in permutation.keys():
            if key == amount_of_lines:
                break
            new_row = copy.deepcopy(permutation[key])
            new_row.append(self.case_utility(new_row,provider,"marginal utility",permutation[amount_of_lines]))
            table.append(new_row)
        # for line in range (0,amount_of_lines):
        #     index = 0
        #     new_row = []
        #     for value in assignments.values():
        #         new_row.append(value[permutation[line][index]])
        #         index+=1
        #     table.append(new_row)
        #     table[line].append(self.case_utility(table,line,provider,"marginal utility"))

        return table

    def case_utility(self,row : list[int],provider : int,policy : string,neighbours) -> int:
        util = 0
        if policy == "marginal utility":
            pass
        else:
            pass
        index = 0
        for i in range(0,len(row)):
            if row[i] == 1:
                    util += self.neighbor_util[neighbours[i]]
            index += 1
        return util

    def ovp(self):
        curerent_util = 0
        for key in self.neighbor_util.keys():
            curerent_util += self.neighbor_util[key]

        diff = 0
        if curerent_util > self.required_utility:
            diff = curerent_util - self.required_utility
        for key in self.neighbor_util.keys():
            self.neighbor_util[key]-= diff/len(self.neighbor_util)


    def select_best_values(self,table : list,provider : int) -> list:
        agent_belief = self.message_data[provider][1].context
        provider_index = 0
        index = 0
        for key in self.neighbor_data.keys():
            if key == provider:
                provider_index = index
            index+=1

        best_lines = {}
        for element in self.neighbor_data[provider][3]:
            best_lines[element] = (0,0)

        for line in table:
            for element in best_lines.keys():
                if line[len(line)-1] > best_lines[element][0] and line[provider_index] == 1:
                    best_lines[element] = (line[len(line)-1] + agent_belief[element],line)

        return best_lines

    def open_mail(self) -> None:
        self.allocated_providers.clear()
        for message in self.inmessagebox:
            if message.sender_id not in self.message_data.keys():
                self.message_data[message.sender_id] = [0,0]
            if isinstance(message, MsgInitFromProvider):
                self.message_data[message.sender_id][0] = message
            if isinstance(message, MsgBeliefVector):
                self.message_data[message.sender_id][1] = message
            if isinstance(message, MsgProviderChoice):
                self.allocated_providers.append((message.sender_id,message.context))
        self.inmessagebox.clear()

    def compute(self):
        self.current_budget = self.utility_budget
        self.open_mail()
        self.nclo = len(self.neighbor_util) * len(self.neighbor_util)
        for provider in self.neighbor_data.keys():
            # produced_table = self.create_value_table(provider)
            # selected_case = self.select_best_values(produced_table,provider)
            self.compile_offers(provider)
            self.act_human(provider)
            self.send_offer_msg(provider)

    def act_human(self,provider):
        '''
        Novelty
        '''
        if random.random() > 1 - self.mistake_probability:
            for i in range(0, int(random.random()*30)):
                self.offer[provider] = utils.rotate_dict(self.offer[provider])


    def send_offer_msg(self, neighbour: int) -> None:
        new_message = MsgUtilityOffer(self.id_, neighbour, self.offer[neighbour])
        self.outmessagebox.append(new_message)

    def generate_result_messages(self):
        for neighbour in self.neighbor_data.keys():
            self.send_offer_msg(neighbour)

    def compile_offers(self,provider : int):
        calculated_offers = {}
        agent_belief = self.message_data[provider][1].context
        for id in agent_belief.keys():
            if id == self.id_:
                total_bel_val = {}
                for bel in  self.message_data.keys():
                    for i in self.message_data[bel][1].context.keys():
                        if i not in total_bel_val:
                            total_bel_val[i] = 0
                        #if i != provider:
                        total_bel_val[i] += self.message_data[bel][1].context[i]

                sum_skills = 0
                for key in self.max_util.keys():
                    sum_skills += self.max_util[key]
                rate_of_util_fall = ((- sum_skills / self.rate_util_fall) / self.max_time)
                sum_util = 0
                for key in self.neighbor_util.keys():
                    if key != provider:
                        sum_util += self.neighbor_util[key]
                max_belief = 0
                for belief in agent_belief.keys():
                    if agent_belief[belief] > max_belief and belief != id:
                        max_belief = agent_belief[belief]

                if sum_util + max_belief > sum_util + self.neighbor_util[provider] + agent_belief[id]:
                    val = 0
                else:
                    f_util = 0
                    for util in self.neighbor_util.keys():
                        if util != provider:
                            f_util += self.neighbor_util[util]
                    if self.required_utility - f_util < 0:
                        f_util = 0
                    else:
                        f_util = min(self.required_utility - f_util, self.neighbor_util[provider])
                    val = f_util #+ agent_belief[id]
                if val < 0:
                    val = 0
                calculated_offers[id] = (val,rate_of_util_fall)
            else:
                 calculated_offers[id] = (0,0)
        self.offer[provider] = calculated_offers


    def calculate_required_utility(self):
        utility = 0
        for key in self.max_util.keys():
            utility += self.max_util[key]
        return utility

    def remove_neighbour(self, agent) -> None:
        super().remove_neighbour(agent)
        if type(agent) == int:
            del self.offer[agent]
        else:
            del self.offer[agent.id_]
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