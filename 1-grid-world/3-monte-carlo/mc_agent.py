import numpy as np
import random
from collections import defaultdict
from environment import Env


class VisitState:
    def __init__(self, name, total_G, N, V):
        self.name = name
        self.total_G = total_G
        self.N = N
        self.V = V

# Monte Carlo Agent which learns every episodes from the sample
class MCAgent:
    def __init__(self, actions):
        self.width = 5
        self.height = 5
        self.actions = actions
        self.discount_factor = 0.9
        self.epsilon = 0.1
        self.samples = []
        self.value_table = defaultdict(float)
        self.visit_state = []

    # append sample to memory(state, reward, done)
    def save_sample(self, state, reward, done):
        self.samples.append([state, reward, done])

    # for every episode, agent updates q function of visited states
    def update(self):
        # state name and G for each state as appeared in the episode
        all_states = []
        G = 0
        for reward in reversed(self.samples):
            state_name = str(reward[0])
            G = reward[1] + self.discount_factor * G
            all_states.append([state_name, G])
        all_states.reverse()

        # use either first visit, every visit or incremental MC
        self.first_visit_mc(all_states)

    def first_visit_mc(self, all_states):
        visit_state = []
        for state in all_states:
            if state[0] not in visit_state:
                visit_state.append(state[0])
                self.update_global_visit_state(state[0], state[1])
        for state in self.visit_state:
            self.value_table[state.name] = state.V

    def every_visit_mc(self, all_states):
        for state in all_states:
                self.update_global_visit_state(state[0], state[1])
        for state in self.visit_state:
            self.value_table[state.name] = state.V

    def incremental_mc(self, all_states):
        for state in all_states:
            self.update_global_visit_state(state[0], state[1], incremental=True)
        for state in self.visit_state:
            self.value_table[state.name] = state.V

    def update_global_visit_state(self, state_name, G_t, incremental = False):
        if not incremental:
            updated = False
            for vs in self.visit_state:
                if vs.name == state_name:
                    vs.total_G = vs.total_G + G_t
                    vs.N = vs.N + 1
                    vs.V = vs.total_G / vs.N
                    updated = True
                    break
            if not updated:
                self.visit_state.append(VisitState(name=state_name, total_G=G_t, N=1, V=G_t))
        else:
            updated = False
            for vs in self.visit_state:
                if vs.name == state_name:
                    vs.N = vs.N + 1
                    learning_rate = 0.5 * 1 / vs.N
                    vs.V = vs.V + learning_rate * (G_t - vs.V)
                    updated = True
                    break
            if not updated:
                self.visit_state.append(VisitState(name=state_name, total_G=None, N=1, V=G_t))


    # get action for the state according to the v function table
    # agent pick action of epsilon-greedy policy
    def get_action(self, state):
        if np.random.rand() < self.epsilon:
            # take random action
            action = np.random.choice(self.actions)
        else:
            # take action according to the q function table
            next_state = self.possible_next_state(state)
            action = self.arg_max(next_state)
        return int(action)

    # compute arg_max if multiple candidates exit, pick one randomly
    @staticmethod
    def arg_max(next_state):
        max_index_list = []
        max_value = next_state[0]
        for index, value in enumerate(next_state):
            if value > max_value:
                max_index_list.clear()
                max_value = value
                max_index_list.append(index)
            elif value == max_value:
                max_index_list.append(index)
        return random.choice(max_index_list)

    # get the possible next states
    def possible_next_state(self, state):
        col, row = state
        next_state = [0.0] * 4

        if row != 0:
            next_state[0] = self.value_table[str([col, row - 1])]
        else:
            next_state[0] = self.value_table[str(state)]
        if row != self.height - 1:
            next_state[1] = self.value_table[str([col, row + 1])]
        else:
            next_state[1] = self.value_table[str(state)]
        if col != 0:
            next_state[2] = self.value_table[str([col - 1, row])]
        else:
            next_state[2] = self.value_table[str(state)]
        if col != self.width - 1:
            next_state[3] = self.value_table[str([col + 1, row])]
        else:
            next_state[3] = self.value_table[str(state)]

        return next_state


# main loop
if __name__ == "__main__":
    env = Env()
    agent = MCAgent(actions=list(range(env.n_actions)))

    for episode in range(1000):
        state = env.reset()
        action = agent.get_action(state)

        while True:
            env.render()

            # forward to next state. reward is number and done is boolean
            next_state, reward, done = env.step(action)
            agent.save_sample(next_state, reward, done)

            # get next action
            action = agent.get_action(next_state)

            # at the end of each episode, update the v function table
            if done:
                print("episode : ", episode)
                agent.update()
                agent.samples.clear()
                break
