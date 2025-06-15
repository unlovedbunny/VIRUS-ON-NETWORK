from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import NetworkModule, ChartModule
from mesa.visualization.UserParam import Slider, NumberInput
from model import VirusModel, network_portrayal

# Módulo de rede para exibir os agentes conectados
network = NetworkModule(network_portrayal, 500, 500)

# Gráfico de evolução dos estados
chart = ChartModule(
    [
        {"Label": "Susceptible", "Color": "#0080FF"},
        {"Label": "Infected", "Color": "#FF0000"},
        {"Label": "Recovered", "Color": "#00FF00"},
    ]
)

# Parâmetros ajustáveis pelo usuário
# Parâmetros ajustáveis pelo usuário
model_params = {
    "num_nodes": NumberInput("Number of Agents", value=100),  # Removidos minimum, maximum e step
    "avg_node_degree": Slider("Avg Node Degree", 3, 1, 10, 1),
    "initial_infected": Slider("Initial Infected (%)", 0.1, 0.01, 1.0, 0.01),
    "virus_check_frequency": Slider("Virus Check Frequency", 1, 1, 10, 1),
    "infection_chance": Slider("Infection Probability", 0.4, 0.0, 1.0, 0.01),
    "recovery_chance": Slider("Recovery Probability", 0.1, 0.0, 1.0, 0.01),
}

# Criando o servidor
server = ModularServer(
    VirusModel,
    [network, chart],
    "Virus on a Network",
    model_params,
)

server.port = 8521
server.launch()
