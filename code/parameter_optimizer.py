from simanneal import Annealer
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import scipy.io as sio
from typing import Dict, Tuple
import pickle as pkl 
import sys
import base_q_learning as bq
from util import *


class data(list): 
    """
    This is a basic class to hold our data and check for equality 
    of a list of actions generated by the agent and generated by the 
    mouse. Later, there will more complex ways of scoring in this class
    """
    actions: np.matrix = None
    all_data = np.matrix = None
    def __init__(self, input_data: list, agent: bool = True): 
        if agent:
            self.actions = np.matrix(input_data)
        else:
            print("Please instantiate a mouse class instead of a data class")
        
        
    def __eq__(self, other): 
        for index in range(len(self.actions)):
            if self.actions[index] != other.actions[index]:
                return False
        return True
        

    def __ne__(self, other):
        return not self.__eq__(other)
    
    
    def score(self, d2):
        assert len(self.actions) == len(data.d2.actions)
        score = 0
        for i in range(len(self.actions)): 
            if self.actions[i] == d2.actions[i]: 
                score += 1
        return score/len(self.actions)
    
    def loss(self):
        """
        The default loss will be cross entropy loss: 
        
        We want to sum over the actions and calculate the -log likelihood
        of the given data (what we are optimizing for) under the generated model. 
        We possibly want to take the average over all of the actions. We can use q
        values as proxies for probabilites (that's effectively what they are)
        """
        pass
    
class mouse(data, Task): 
    def __init__(self, matlab_url):
        mat = sio.loadmat(matlab_url)
        self.result = mat['group_setsize2_result'][0][0][0]
        self.rewards = mat['group_setsize2_reward'][0][0][0]
        self.ports = mat['group_setsize2_portside'][0][0][0]
        self.odors = mat['group_setsize2_odors'][0]
        self.schedule = mat['group_setsize2_schedule'][0][0][0]
        self.all = list(zip(self.result, self.rewards, self.ports, self.schedule))
        self.actions = list(set(self.ports))
        self.odors = [str(i[0]) for i in list(self.odors)]
        self.states = list(set(self.schedule))
        
    def make_action(self, state: str, action: str, i: int = 0) -> Tuple[str, float]:
        if str(self.ports[i]) == str(action): 
            reward: float = 10 
        else: 
            reward: float = -1
        new_state: str = self.schedule[i]
        return (new_state, reward)
    def get_legal_actions(self, state: str) -> List[str]:
        return self.actions
    
        
    


class parameter_optimizer(Annealer): 
    """
    This class will run simulated annealing
    in order to find the correct parameters for a single mouse
    """

    state = None
    def __init__(self, matlab_url):
        self.m = mouse(matlab_url)
        self.state = bq.q_learning_agent(task = self.m, initial_state = 3, iterations = len(self.m.all))
    def move (self):
        """
        Changes the parameters randomly
        """
        coin_flip = random.randint(0,2)
        self.state.parameters.set_random_params()
        self.state.initialize_q_params()
    def energy(self):
        self.state.run_q_learning()
        count = 0
        for i in range(len(self.m.all)):
            got_reward = bool(self.m.rewards[i])
            
            if got_reward:
                mouse_action = self.m.ports[i]
            else:
                mouse_action = int(list(set([a for a in self.m.ports if a!=self.m.ports[i]]))[0])
                
            if mouse_action != self.state.actions[i]:
                count += 1
                
        
        return count
    
    
    
if __name__ == '__main__':
    m = parameter_optimizer('../data/pilot_data_2odor_8020prob.mat')
    m.Tmax = 500.0  # Max (starting) temperature
    m.Tmin = 2.5      # Min (ending) temperature
    m.steps = 5000   # Number of iterations
    m.updates = 10000   # Number of updates (by default an update prints to stdout)
    agent = m.anneal()
    alpha = "alpha:" + str(agent.parameters.alpha)
    epsilon = "epsilon:" + str(agent.parameters.epsilon)
    outfile = open("../output/test.txt", 'rw+')
    outfile.write(alpha + "\n" + epsilon)
    



