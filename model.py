from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import networkx as nx
import random

class VirusAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.state = "S"  # S = Susceptible, I = Infected, R = Recovered

    def step(self):
        if self.state == "I":
            # Infect neighbors
            for neighbor in self.model.G.neighbors(self.unique_id):
                neighbor_agent = self.model.schedule.agents[neighbor]
                if neighbor_agent.state == "S":
                    if random.random() < self.model.virus_spread_chance:
                        neighbor_agent.state = "I"

            # Recover
            if random.random() < self.model.recovery_chance:
                self.state = "R"

class VirusModel(Model):
    def __init__(self, num_nodes, avg_node_degree, initial_infected,
                 virus_check_frequency=1, infection_chance=0.4, recovery_chance=0.1):
        self.num_nodes = num_nodes
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=avg_node_degree/self.num_nodes)
        self.schedule = RandomActivation(self)
        self.virus_spread_chance = infection_chance
        self.recovery_chance = recovery_chance

        # Create agents
        for i in range(self.num_nodes):
            a = VirusAgent(i, self)
            self.schedule.add(a)
            self.G.nodes[i]["agent"] = a  # Associate agent with node

        # Infect some initial agents
        initial_infected = int(initial_infected * self.num_nodes)
        infected_nodes = self.random.sample(range(self.num_nodes), initial_infected)
        for node in infected_nodes:
            self.schedule.agents[node].state = "I"

        # Data collection setup - CORRIGIDO
        self.datacollector = DataCollector(
            model_reporters={
                "Susceptible": lambda m: sum(1 for a in m.schedule.agents if a.state == "S"),
                "Infected": lambda m: sum(1 for a in m.schedule.agents if a.state == "I"),
                "Recovered": lambda m: sum(1 for a in m.schedule.agents if a.state == "R")
            }
        )

    def step(self):
        self.datacollector.collect(self)  # Coletar ANTES do passo
        self.schedule.step()

def network_portrayal(G):
    portrayal = {"nodes": [], "edges": []}
    
    for node in G.nodes():
        agent = G.nodes[node].get("agent", None)
        color = "#808080"  # Gray for None/default
        
        if agent:
            if agent.state == "S":
                color = "#0080FF"  # Blue
            elif agent.state == "I":
                color = "#FF0000"  # Red
            elif agent.state == "R":
                color = "#00FF00"  # Green

        portrayal["nodes"].append({
            "id": node,
            "color": color,
            "size": 6,
            "tooltip": f"State: {agent.state if agent else 'None'}"
        })

    for edge in G.edges():
        portrayal["edges"].append({
            "source": edge[0],
            "target": edge[1],
            "color": "#CCCCCC"
        })

    return portrayal