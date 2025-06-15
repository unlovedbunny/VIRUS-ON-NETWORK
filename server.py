from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import NetworkModule, ChartModule
from mesa.visualization.UserParam import Slider, NumberInput
from model import VirusModel, network_portrayal

# Módulo de rede para exibir os agentes conectados
network = NetworkModule(network_portrayal, 500, 500)

# Gráfico de evolução dos estados ATUALIZADO
chart = ChartModule(
    [
        {"Label": "Susceptible", "Color": "#0080FF"},
        {"Label": "Infected", "Color": "#FF0000"},
        {"Label": "Recovered", "Color": "#00FF00"},
        {"Label": "Vaccinated", "Color": "#9400D3"}, 
        {"Label": "Dead", "Color": "#000000"},       
    ]
)

model_params = {
    "num_nodes": NumberInput("Number of Agents", value=100),
    "avg_node_degree": Slider("Avg Node Degree", value=3, min_value=1, max_value=10, step=1),
    "initial_infected": Slider("Initial Infected (%)", value=0.1, min_value=0.01, max_value=1.0, step=0.01),
    "infection_chance": Slider("Infection Probability", value=0.4, min_value=0.0, max_value=1.0, step=0.01),
    "recovery_chance": Slider("Recovery Probability", value=0.1, min_value=0.0, max_value=1.0, step=0.01),
    # --- NOVOS SLIDERS ---
    "death_chance": Slider("Death Probability", value=0.02, min_value=0.0, max_value=0.1, step=0.001),
    "vaccination_rate": Slider("Vaccination Rate (per step)", value=0.05, min_value=0.0, max_value=1.0, step=0.01),
}

server = ModularServer(
    VirusModel,
    [network, chart],
    "Virus on Network", # Título atualizado
    model_params,
)

server.port = 8521
server.launch()