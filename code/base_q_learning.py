import numpy as np
from typing import *
import random
import matplotlib.pyplot as plt
from util import *


class Parameters:
    """
    This is just a shell class to hold the parameters
    """
    learning_rate: float = 0 #alpha, how quick the agent learns
    discount_factor: float = 0 # discount rate
    exploration_prob: float = 0 #epsilon
    tau: float = 0
    def __init__(self):
        self.learning_rate = lambda x: random.uniform(0, 1)
        self.discount_faction = random.uniform(0, 1)
        self.exploration_prob = random.uniform(0, 1)
        self.tau = np.random.exponential(5)
        self.delta = random.uniform(0,1)
        self.sigma = np.random.exponential(5)
    def set_params(self, learning_rate: float, discount_factor: float) -> None:
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        
    def set_learning_rate(self, alpha: float) -> None:
        self.learning_rate = alpha
        
    def set_discount_factor(self, gamma: float) -> None: 
        self.discount_factor = gamma
        

    def set_random_params(self) -> None:
        self.__init__()



class q_learning_agent:
    q_values: Dict[Tuple[str, str], float] = {}
    task: Task = None
    current_state: str = None
    all_q_vals: List[Dict] = []
    state_list: List[str] = []
    action_probs = []
    def __init__(self, iterations: int = 1000, task: Task = None, initial_state: str = None, \
                 parameters: Parameters = Parameters()) -> None:
        self.iterations = iterations
        self.parameters = parameters
        self.task = task
        self.current_state =initial_state 
        self.initialize_q_params()
        
    def initialize_q_params(self) -> None:
        #for key in self.task.transitions:
        #    self.q_values[key] = 0
        for state in self.task.states:
            for actions in self.task.actions:
                self.q_values[(state,actions)] = 0
                
        self.all_q_vals = []
        self.action_probs = []
                
    def update_q_values(self, state, action, next_state, reward, iteration) -> None: 
        alpha = self.parameters.learning_rate(iteration)
        gamma = self.parameters.discount_factor
        next_state_q_vals = {key:value for (key,value) in self.q_values.items() if next_state in key}
        old_q = self.q_values[(state, action)]
        new_q = (1-alpha) * old_q + alpha * (reward + gamma *\
                                             next_state_q_vals[max(next_state_q_vals, key = next_state_q_vals.get)])
        self.q_values[(state, action)] = new_q
        
        
    def generate_action_probs(self) -> None: 
        action_prob_dict: Dict[Tuple[str,str], float]
        action_prob_dict = {}
        epsilon = self.parameters.exploration_prob
        for state in self.task.states: 
            curr_state_qvals = {key:value for (key,value) in self.q_values.items() if state in key}
            max_action = max(curr_state_qvals, key = curr_state_qvals.get)
            for key in curr_state_qvals: 
                if key[1] == max_action[1]:
                    action_prob_dict[key] = np.log(epsilon/len(self.task.actions) + (1-epsilon))
                else: 
                    action_prob_dict[key] = np.log(epsilon/len(self.task.actions))

        self.action_probs.append(action_prob_dict)
            
    def choose_action(self, state) -> str:

        legal_actions = self.task.get_legal_actions(state)
        num = random.uniform(0, 1)
        if num <= self.parameters.exploration_prob:
            return random.choice(legal_actions)
        
        state_q_values =  {key:value for (key,value) in self.q_values.items() if state in key}
        return max(self.q_values, key= self.q_values.get)[1]
        
    def run_q_learning(self) -> list:
        self.actions = []
        actions: List[str]  = []
        i: int = 0
        while i < self.iterations:
            
            action = self.choose_action(self.current_state)
            actions.append(action)
            next_state, reward = self.task.make_action(self.current_state, action, i)
            self.update_q_values(self.current_state, action, next_state, reward, iteration = i)
            self.all_q_vals.append(self.q_values)
            #print("The current state is: " + str(self.current_state))
            #print("The given action is: " + str(action))
            #print("The q values are as follows:" +str(self.q_values))
            #print("Reward for next state is: " + str(reward))
            #print("\n\n\n")
            self.generate_action_probs()
            self.current_state = next_state
            self.actions.append(action)
            #print(i)
            i+=1
        return actions
    def AIC(self, likelihood):
        num_parameters = 3
        return 2*num_parameters - 2*likelihood
    
    
    
    
class softmax_agent(q_learning_agent):
    def choose_action(self, state) -> str: 
        legal_actions = self.task.get_legal_actions(state)
        qvals = {key:value for (key,value) in self.q_values.items() if state in key}
        softmax_probs = self.softmax(qvals)

        prob_list = []
        key_list = []
        for key in qvals:
            prob_list.append(softmax_probs[key])
            key_list.append(key[1])
        #for i in range(len(prob_list)): 
        #    if np.isnan(prob_list[i]):
        #        prob_list[i] = 1
        self.action_probs.append({key: np.log(value) for (key, value) in softmax_probs.items()})
        return np.random.choice(key_list, p =prob_list)
            
    def softmax(self, qvals):
        # USE Stable softmax instead as it protects against numerical instability
        beta_val = self.parameters.tau
        max_q = max(qvals.values())
        sum_qs= sum([np.exp((qvals[x] - max_q)*beta_val) for x in qvals])

        
        softmax_dict = {}
        for key in qvals:
            curr_ex = np.exp((qvals[key] - max_q)*beta_val)
            softmax_dict[key] = curr_ex/sum_qs

            #print(softmax_dict)
        #print("Probability", softmax_dict)
        return softmax_dict
    