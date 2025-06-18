from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import networkx as nx
import random

class VirusAgent(Agent):
  
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.state = "S"
        self.days_exposed = 0
        self.days_infected = 0
        
        # Atributos de vacinação
        self.is_vaccinated = False
        self.vaccine_type = None
        # Eficácia da vacina em prevenir a infecção (S -> E)
        self.vaccine_efficacy_infection = 0.0
        # Eficácia da vacina em prevenir a doença grave (E -> I)
        self.vaccine_efficacy_progression = 0.0

    def step(self):
        # Estados terminais: se o agente está Recuperado ou Morto, não faz mais nada.
        if self.state in ["R", "D"]:
            return

        # Lógica de transição temporal
        if self.state == "E":
            self.days_exposed += 1
            if self.days_exposed >= self.model.incubation_period:
                # Após o período de incubação, a vacina pode impedir a progressão para infecção
                if random.random() < self.vaccine_efficacy_progression:
                    self.state = "R" # Vacina eficaz, agente recupera sem se tornar infeccioso
                else:
                    self.state = "I" # Vacina não foi eficaz, agente se torna infeccioso
        elif self.state == "I":
            self.spread_virus()
            self.days_infected += 1
            if self.days_infected >= self.model.infection_duration:
                if random.random() < self.model.mortality_rate:
                    self.state = "D"
                else:
                    self.state = "R"

    def spread_virus(self):
        """Um agente infectado (I) tenta infectar seus vizinhos suscetíveis (S)."""
        for neighbor_id in self.model.G.neighbors(self.unique_id):
            neighbor = self.model.schedule._agents[neighbor_id] 
            if neighbor.state == "S":
                # A eficácia da vacina do vizinho reduz a chance de infecção
                infection_prob = self.model.infection_chance * (1 - neighbor.vaccine_efficacy_infection)
                if random.random() < infection_prob:
                    neighbor.state = "E"

    def vaccinate(self, vaccine_type):
        """Aplica a vacina a um agente, definindo sua eficácia."""
        if self.state == "S": # Só vacina suscetíveis
            self.is_vaccinated = True
            self.vaccine_type = vaccine_type
            if self.vaccine_type == "Pfizer":
                self.vaccine_efficacy_infection = self.model.pfizer_efficacy_infection
                self.vaccine_efficacy_progression = self.model.pfizer_efficacy_progression
            elif self.vaccine_type == "Oxford":
                self.vaccine_efficacy_infection = self.model.oxford_efficacy_infection
                self.vaccine_efficacy_progression = self.model.oxford_efficacy_progression
            
            self.state = "V" # Novo estado para "Vacinado-Suscetível"

class VirusModel(Model):
   
    def __init__(self, num_nodes=100, network_type='barabasi_albert', avg_node_degree=3, 
                 initial_infected=5, infection_chance=0.05, 
                 incubation_period=5, infection_duration=10, mortality_rate=0.02,
                 vaccination_start_day=20, daily_vaccinations=10,
                 pfizer_efficacy_infection=0.8, oxford_efficacy_infection=0.6,
                 pfizer_efficacy_progression=0.9, oxford_efficacy_progression=0.75):
        
        super().__init__()
        self.num_nodes = num_nodes
        
        if network_type == 'barabasi_albert':
            self.G = nx.barabasi_albert_graph(n=self.num_nodes, m=avg_node_degree)
        else: 
            self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=avg_node_degree / self.num_nodes)
            
        self.schedule = RandomActivation(self)
        

        self.infection_chance = infection_chance
        self.incubation_period = incubation_period
        self.infection_duration = infection_duration
        self.mortality_rate = mortality_rate
        self.vaccination_start_day = vaccination_start_day
        self.daily_vaccinations = daily_vaccinations
        self.pfizer_efficacy_infection = pfizer_efficacy_infection
        self.oxford_efficacy_infection = oxford_efficacy_infection
        self.pfizer_efficacy_progression = pfizer_efficacy_progression
        self.oxford_efficacy_progression = oxford_efficacy_progression

        # Criando os agentes
        for i, node in enumerate(self.G.nodes()):
            a = VirusAgent(i, self)
            self.schedule.add(a)
            self.G.nodes[node]["agent"] = a

        # Infectando uma parcela inicial
        infected_nodes = self.random.sample(list(self.G.nodes()), initial_infected)
        for agent in self.schedule.agents:
            if agent.unique_id in infected_nodes:
                agent.state = "E"

        self.datacollector = DataCollector(
            model_reporters={
                "Susceptible": lambda m: sum(1 for a in m.schedule.agents if a.state == "S"),
                "Vaccinated": lambda m: sum(1 for a in m.schedule.agents if a.state == "V"),
                "Exposed": lambda m: sum(1 for a in m.schedule.agents if a.state == "E"),
                "Infected": lambda m: sum(1 for a in m.schedule.agents if a.state == "I"),
                "Recovered": lambda m: sum(1 for a in m.schedule.agents if a.state == "R"),
                "Dead": lambda m: sum(1 for a in m.schedule.agents if a.state == "D"),
            })

    def run_vaccination_campaign(self):
        """Procedimento para vacinar uma parcela da população a cada dia."""
        susceptible_agents = [a for a in self.schedule.agents if a.state == "S"]
        # Embaralha para vacinar aleatoriamente
        random.shuffle(susceptible_agents)
        
        # Vacina um número definido de agentes por dia
        agents_to_vaccinate = susceptible_agents[:self.daily_vaccinations]
        
        for agent in agents_to_vaccinate:
            # Assume uma distribuição 50/50 das vacinas
            if random.random() < 0.5:
                agent.vaccinate("Pfizer")
            else:
                agent.vaccinate("Oxford")

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        if self.schedule.steps >= self.vaccination_start_day:
            self.run_vaccination_campaign()


def network_portrayal(G):

    portrayal = {"nodes": [], "edges": []}
    for node, data in G.nodes(data=True):
        agent = data.get("agent")
        if not agent: continue
        color_map = {
            "S": "#0080FF", "E": "#F4D03F", "I": "#FF0000",
            "R": "#00FF00", "D": "#000000", "V": "#9400D3"
        }
        color = color_map.get(agent.state, "#808080")
        tooltip = f"ID: {agent.unique_id}<br>State: {agent.state}"
        if agent.is_vaccinated:
            tooltip += f"<br>Vaccine: {agent.vaccine_type}"
        portrayal["nodes"].append({"id": node, "color": color, "size": 6, "tooltip": tooltip})
    for source, target in G.edges():
        portrayal["edges"].append({"source": source, "target": target, "color": "#CCCCCC"})
    return portrayal