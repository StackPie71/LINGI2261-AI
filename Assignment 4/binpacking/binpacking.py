#! /usr/bin/env python3
"""NAMES OF THE AUTHOR(S): Gaël Aglin <gael.aglin@uclouvain.be>"""
from search import *
import sys
import time
import numpy as np


class BinPacking(Problem):
    # Possible moves =
    # - items which can be moved in another bin
    # - swap of two items (To be done)
    def successor(self, state):
        successors = []
        for i in range(len(state.bins)):
            for ind, size in list(state.bins[i].items()):
                # ind, size = list(state.bins[i].items())  # We take only the item on top of the bin
                for j in range(len(state.bins)):
                    if j != i:
                        # we move an item into a different bin
                        if state.can_fit(state.bins[j], size):
                            new_state = state.copy()
                            new_state.bins[j][ind] = size
                            new_state.bins[i].pop(ind)
                            successors.append(('move', new_state))

                        # we swap two items
                        for ind_swap, size_swap in list(state.bins[j].items()):
                            # ind_swap, size_swap = list(state.bins[j].items())[-1]
                            new_state_swap = state.copy()
                            new_state_swap.bins[i].pop(ind)
                            new_state_swap.bins[j].pop(ind_swap)
                            # If we can swap these items
                            if new_state_swap.can_fit(new_state_swap.bins[j], size) and new_state_swap.can_fit(
                                    new_state_swap.bins[i], size_swap):
                                new_state_swap.bins[i][ind_swap] = size_swap
                                new_state_swap.bins[j][ind] = size
                                successors.append(('swap', new_state_swap))

        return successors

    def fitness(self, state):
        """
        :param state:
        :return: fitness value of the state in parameter
        """
        # We delete empty bins
        non_empty_bins = []
        for check_bin in state.bins:
            if check_bin:
                non_empty_bins.append(check_bin)
        state.bins = non_empty_bins

        fullness = []
        nums = []
        for bin_i in state.bins:
            sum = 0
            for value in bin_i.values():
                sum += value
            fullness.append(sum)
            nums.append((sum / state.capacity) ** 2)
        sum2 = 0
        for num in nums:
            sum2 += num
        fit = 1 - sum2 / len(state.bins)

        return fit


class State:

    def __init__(self, capacity, items, bins=None):
        self.capacity = capacity
        self.items = items
        if bins is None:
            self.bins = self.build_init()
        else:
            self.bins = bins

    # an init state building is provided here but you can change it at will
    def build_init(self):
        init = []
        for ind, size in self.items.items():
            if len(init) == 0 or not self.can_fit(init[-1], size):
                init.append({ind: size})
            else:
                if self.can_fit(init[-1], size):
                    init[-1][ind] = size
        return init

    def can_fit(self, bin, itemsize):
        return sum(list(bin.values())) + itemsize <= self.capacity

    def copy(self):
        new_bins = []
        for bin1 in self.bins:
            new_bins.append(dict(bin1))

        return State(self.capacity, self.items.copy(), new_bins)

    def __str__(self):
        s = ''
        for i in range(len(self.bins)):
            s += ' '.join(list(self.bins[i].keys())) + '\n'
        return s

    def compare(self, other):
        # Return True if the two state are the same, else return False
        if len(self.bins) != len(other.bins):
            return False
        else:
            counter1 = 0
            for i in range(len(self.bins)):
                if self.bins[i] == other.bins[i]:
                    counter1 += 1
            if counter1 == len(self.bins):
                return True
            else:
                return False


def read_instance(instanceFile):
    file = open(instanceFile)
    capacitiy = int(file.readline().split(' ')[-1])
    items = {}
    line = file.readline()
    while line:
        items[line.split(' ')[0]] = int(line.split(' ')[1])
        line = file.readline()
    return capacitiy, items


def explored(state_conf, explored_conf):
    # Look if the current state has not been already explored
    for explo in explored_conf:
        if state_conf.compare(explo):
            return True
    return False


# Attention : Depending of the objective function you use, your goal can be to maximize or to minimize it
def maxvalue(problem, limit=100, callback=None):
    current = LSNode(problem, problem.initial, 0)
    best = current
    best_step = 0
    for step in range(limit):
        if callback is not None:
            callback(current)
        expanded = list(current.expand())
        current = expanded[0]
        for next_node in expanded:
            if problem.fitness(next_node.state) < problem.fitness(current.state):
                current = next_node
        if problem.fitness(current.state) < problem.fitness(best.state):
            best = current
            best_step = step

    return best, best_step


# Attention : Depending of the objective function you use, your goal can be to maximize or to minimize it
def randomized_maxvalue(problem, limit=100, callback=None):
    current = LSNode(problem, problem.initial, 0)
    best = current
    best_step = 0
    for step in range(limit):
        if callback is not None:
            callback(current)
        expanded = list(current.expand())
        current = expanded[0]
        best_5 = expanded[:4]
        for next_node in expanded:
            for i in range(len(best_5)):
                if problem.fitness(next_node.state) < problem.fitness(best_5[i].state):
                    best_5[i] = next_node
                    break
        current = random.choice(best_5)
        if problem.fitness(current.state) < problem.fitness(best.state):
            best = current
            best_step = step

    return best, best_step


def random_walk(problem, limit=100, callback=None):
    """Perform a random walk in the search space and return the best solution
    found. The returned value is a Node.
    If callback is not None, it must be a one-argument function that will be
    called at each step with the current node.
    """
    current = LSNode(problem, problem.initial, 0)
    best = current
    best_step = 0
    for step in range(limit):
        if callback is not None:
            callback(current)
        current = random.choice(list(current.expand()))
        if problem.fitness(current.state) > problem.fitness(best.state):
            best = current
            best_step = step

    return best, best_step


#####################
#       Launch      #
#####################
# if __name__ == '__main__':
#     info = read_instance(sys.argv[1])
#     init_state = State(info[0], info[1])
#     bp_problem = BinPacking(init_state)
#     step_limit = 100
#     node = randomized_maxvalue(bp_problem, step_limit)
#     state = node.state
#     print(state)

info = read_instance("instances/i10.txt")
init_state = State(info[0], info[1])
bp_problem = BinPacking(init_state)
step_limit = 100

times = []
fitnesses = []
steps = []
for i in range(10):
    start_time = time.time()
    node, number_step = randomized_maxvalue(bp_problem, step_limit)
    end_time = time.time()
    state = node.state
    times.append(end_time - start_time)
    fitnesses.append(bp_problem.fitness(state))
    steps.append(number_step)

print("Mean time:", np.mean(times))
print("Mean fitness:", np.mean(fitnesses))
print("Mean steps:", np.mean(steps))

# print("Time:", end_time - start_time)
# print("Step:", number_step)
#
# print("Fitness:", bp_problem.fitness(state))
# print(state)
