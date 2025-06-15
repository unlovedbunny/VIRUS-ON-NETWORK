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
        # Estados terminais: se o agente já está Recuperado, Vacinado ou Morto, não faz mais nada.
        if self.state in ["R", "V", "D"]:
            return

        # Lógica para agentes SUSCETÍVEIS
        if self.state == "S":
            if random.random() < self.model.vaccination_rate:
                self.state = "V"
                return # Termina o turno do agente se ele for vacinado

            for neighbor_id in self.model.G.neighbors(self.unique_id):
                neighbor_agent = self.model.G.nodes[neighbor_id]["agent"]
                if neighbor_agent.state == "I":
                    if random.random() < self.model.infection_chance:
                        self.state = "I"
                        return # Termina o turno do agente ao ser infectado
        
        # Lógica para agentes INFECTADOS
        if self.state == "I":
            if random.random() < self.model.death_chance:
                self.state = "D"
                return # Termina o turno do agente se ele morrer

            
            if random.random() < self.model.recovery_chance:
                self.state = "R"

class VirusModel(Model):
    def __init__(self, num_nodes, avg_node_degree, initial_infected, infection_chance=0.4, 
                 recovery_chance=0.1, death_chance=0.02, vaccination_rate=0.05): 
        
        self.num_nodes = num_nodes
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=avg_node_degree / self.num_nodes)
        self.schedule = RandomActivation(self)
        
        # Guardando todos os parâmetros
        self.infection_chance = infection_chance
        self.recovery_chance = recovery_chance
        self.death_chance = death_chance         
        self.vaccination_rate = vaccination_rate 
        
        self.running = True

        for i, node in enumerate(self.G.nodes()):
            a = VirusAgent(i, self)
            self.schedule.add(a)
            self.G.nodes[node]["agent"] = a

    
        initial_infected_count = int(initial_infected * self.num_nodes)
        infected_nodes = self.random.sample(list(self.G.nodes()), initial_infected_count)
        for node in infected_nodes:
            self.G.nodes[node]["agent"].state = "I"

        self.datacollector = DataCollector(
            model_reporters={
                "Susceptible": lambda m: sum(1 for a in m.schedule.agents if a.state == "S"),
                "Infected": lambda m: sum(1 for a in m.schedule.agents if a.state == "I"),
                "Recovered": lambda m: sum(1 for a in m.schedule.agents if a.state == "R"),
                "Vaccinated": lambda m: sum(1 for a in m.schedule.agents if a.state == "V"), 
                "Dead": lambda m: sum(1 for a in m.schedule.agents if a.state == "D"),       
            }
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

def network_portrayal(G):
    portrayal = {"nodes": [], "edges": []}
    
    for node, data in G.nodes(data=True):
        agent = data.get("agent")
        if not agent: continue

        color = "#808080"
        if agent.state == "S": color = "#0080FF"  # Azul (Sucetivel)
        elif agent.state == "I": color = "#FF0000"  # Vermelho (Infectado)
        elif agent.state == "R": color = "#00FF00"  # Verde (REcuperado)
        elif agent.state == "V": color = "#9400D3"  # Roxo (Vacinado) 
        elif agent.state == "D": color = "#000000"  # Preto (Morto)  

        portrayal["nodes"].append({
            "id": node,
            "color": color,
            "size": 6,
            "tooltip": f"ID: {agent.unique_id}<br>State: {agent.state}"
        })

    for source, target in G.edges():
        portrayal["edges"].append({
            "source": source,
            "target": target,
            "color": "#CCCCCC"
        })

    return portrayal