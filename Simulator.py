import copy

import pandas
from tqdm import tqdm

from MSSO_Mailer import MSSO_Mailer
from Problem import Problem
from graphics import *

# creates all instances of problem
from utils import plot_xy_graph


def create_problems(algorithm, utility_type, number_of_problems, number_of_providers,
                    number_of_requesters, random_params, distance_threshold, num_skill_types, max_skill_ability_needed,
                    max_skill_ability_provided, max_capacity_per_skill, mean_time_per_skill, max_time_per_requester,
                    utility_threshold_for_acceptance):
    ans = []
    for i in range(number_of_problems):
        problem_i = Problem(prob_id=i, algorithm=algorithm, utility_type=utility_type,
                            number_of_providers=number_of_providers, number_of_requesters=number_of_requesters,
                            random_params=random_params, distance_threshold=distance_threshold,
                            num_skill_types=num_skill_types, max_skill_ability_needed=max_skill_ability_needed,
                            max_skill_ability_provided=max_skill_ability_provided,
                            max_capacity_per_skill=max_capacity_per_skill, mean_time_per_skill=mean_time_per_skill,
                            max_time_per_requester=max_time_per_requester,
                            utility_threshold_for_acceptance=utility_threshold_for_acceptance)
        ans.append(problem_i)
    return ans

def set_colors(problem : Problem):
    for requester in problem.requesters:
        if list(requester.neighbor_data.keys()) == []:
            requester.graphic.setFill("yellow")
        else:
            requester.graphic.setFill("white")
    for provider in problem.providers:
        if list(provider.neighbor_data.keys()) == []:
            provider.graphic.setFill("yellow")
        else:
            provider.graphic.setFill("white")

def draw_problem_graph(win : GraphWin, problem : Problem):
    for requester in problem.requesters:
        if list(requester.neighbor_data.keys()) == []:
            requester.graphic.setFill("yellow")
        else:
            requester.graphic.setFill("white")
        requester.graphic.draw(win)
        id_text = Text(Point(requester.current_location[0], requester.current_location[1]),"R"+str(requester.id_))
        id_text.draw(win)

    for provider in problem.providers:
        provider.graphic.draw(win)
        id_text = Text(Point(provider.current_location[0], provider.current_location[1]), "P" + str(provider.id_))
        id_text.draw(win)
        for key in provider.connections.keys():
            thisline = Line(Point(provider.current_location[0], provider.current_location[1]),
                 Point(provider.connections[key][0], provider.connections[key][1])).draw(win)
            if provider.chosen_requesters != [] and provider.chosen_requesters[0][0] == key:
                thisline.setFill("red")
                thisline.setOutline("red")

# creates mailer and solves problems
def solve_problems(win,problems_input, mailer_iteration_termination):
    utilities_per_problem = []
    i = 0
    for problem in problems_input:
            copy_problem = copy.deepcopy(problem)
            mailer = MSSO_Mailer(copy_problem,mailer_iteration_termination,euclidian_distance_threshold)
            set_colors(copy_problem)

            mailer.initiate()

            res = []
            for p in range(0,mailer_iteration_termination):
                    # draw_problem_graph(win, copy_problem)
                    iter_res = mailer.iterate()
                    if res != []:
                        res.append((iter_res[0],iter_res[1] + res[-1][1]))
                    else:
                        res.append(iter_res)
                    # time.sleep(1.5)
                    # win.clear()

            utilities_per_problem.append(res)
            mx = max(utilities_per_problem[i])
            print(mx)

            i+=1


    return utilities_per_problem


if __name__ == "__main__":
    # algorithm variables
    algorithm = 0  # 0=maxsum
    mailer_iteration_termination = 100
    utility_type = 0  # 0= iterative, 1=gale-shapley, 2=according to location,

    # problem variables
    number_of_problems = 30
    number_of_providers = 10
    number_of_requesters = 15
    location_min_x = 1
    location_max_x = 50
    location_min_y = 1
    location_max_y = 50
    travel_speed = 50  # km per hour
    euclidian_distance_threshold = 1000  # who can be my neighbor - within euc distance
    num_skill_types = 4
    max_skill_ability_needed = 10  # how much of the skill does the requester need
    max_skill_ability_provided = 3  # how much of the skill does the provider have
    max_capacity_per_skill = 2  # max for cap function
    min_util_threshold = 750
    max_util_threshold = 2000
    max_time_per_requester = 5  # [hours] time fluctuation (from min needed to min needed + max_time_per_requester)
    mean_time_per_skill = 1  # time it takes to complete one skill unit
    utility_threshold_for_acceptance = 5  # less than this number = not worth the effort

    # helps reduce input variables
    random_params = {"location_min_x": location_min_x, "location_max_x": location_max_x,
                     "location_min_y": location_min_y, "location_max_y": location_max_y,
                     "min_util_threshold": min_util_threshold, "max_util_threshold": max_util_threshold,
                     "travel_speed": travel_speed}

    # specifically
    problems = create_problems(algorithm=algorithm,
                               utility_type=utility_type, number_of_problems=number_of_problems,
                               number_of_providers=number_of_providers, number_of_requesters=number_of_requesters,
                               random_params=random_params, distance_threshold=euclidian_distance_threshold,
                               num_skill_types=num_skill_types, max_skill_ability_needed=max_skill_ability_needed,
                               max_skill_ability_provided=max_skill_ability_provided,
                               max_capacity_per_skill=max_capacity_per_skill, mean_time_per_skill=mean_time_per_skill,
                               max_time_per_requester=max_time_per_requester,
                               utility_threshold_for_acceptance=utility_threshold_for_acceptance)




    win = GraphWin(width=800, height=800)  # create a window
    win.setCoords(-5, -5, 55, 55)  # set the coordinates of the window; bottom left is (-5, -5) and top right is (55, 55)
    utilities_per_problem = solve_problems(win,problems_input=problems, mailer_iteration_termination=mailer_iteration_termination)
    win.close()

    avg = []

    nclo_stamps = []
    for utils in tqdm(utilities_per_problem):
        for i in utils:
            if i[1] not in nclo_stamps:
                nclo_stamps.append(i[1])
    nclo_stamps = sorted(nclo_stamps)

    for utils in tqdm(utilities_per_problem):
        index_in_nclso = 0
        for i in nclo_stamps:
            x = -1
            for item in utils:
                if item[1] == i:
                    x = 1
                    break
            if x == 1:
                utils.append((utils[index_in_nclso][0], i))
                index_in_nclso += 1
        utils.sort(key=lambda y: y[1])

    for i in range(0, len(nclo_stamps)):
        avg.append(0)

    for problem_utils in tqdm(utilities_per_problem):
        index = 0
        for i in problem_utils:
            if index >= len(nclo_stamps):
                break
            avg[index] += i[0]
            index += 1
    for i in range(0, len(avg)):
        avg[i] = avg[i] / len(utilities_per_problem)

    plot_xy_graph(avg, nclo_stamps)
    any_time = []
    max = 0
    for util in tqdm(avg):
        if util > max:
            max = util
        any_time.append(max)
    plot_xy_graph(any_time, nclo_stamps)

    pandas.DataFrame((any_time, nclo_stamps)).to_csv('anytime.csv')
    pandas.DataFrame((avg, nclo_stamps)).to_csv('data.csv')