# server.py

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import NetworkModule, ChartModule
from mesa.visualization.UserParam import Slider, NumberInput, Choice
from model import VirusModel, network_portrayal

# Módulo de rede
network = NetworkModule(network_portrayal, 500, 500)

# Gráfico de evolução SEIRD + Vacinados
chart = ChartModule([
    {"Label": "Susceptible", "Color": "#0080FF"},
    {"Label": "Exposed", "Color": "#F4D03F"},
    {"Label": "Infected", "Color": "#FF0000"},
    {"Label": "Recovered", "Color": "#00FF00"},
    {"Label": "Vaccinated", "Color": "#9400D3"},
    {"Label": "Dead", "Color": "#000000"},
])

# Parâmetros do modelo ajustáveis
model_params = {
    "num_nodes": NumberInput("Número de Agentes", value=200),
    "network_type": Choice("Tipo de Rede", value='barabasi_albert', choices=['Modelo de Rede Aleatória', 'Modelo de Rede Livre de Escala']),
    "avg_node_degree": Slider("Grau Médio de Conexão", value=4, min_value=1, max_value=20, step=1),
    "initial_infected": NumberInput("Nº Inicial de Expostos", value=5),
    "infection_chance": Slider("Prob. de Infecção por Contato", value=0.05, min_value=0.0, max_value=0.2, step=0.01),
    "incubation_period": NumberInput("Período de Incubação (dias)", value=5),
    "infection_duration": NumberInput("Duração da Infecção (dias)", value=10),
    "mortality_rate": Slider("Taxa de Mortalidade", value=0.02, min_value=0.0, max_value=0.1, step=0.001),
    "vaccination_start_day": NumberInput("Dia de Início da Vacinação", value=20),
    "daily_vaccinations": NumberInput("Nº de Vacinas por Dia", value=10),
    "pfizer_efficacy_infection": Slider("Eficácia Pfizer (Infecção)", value=0.80, min_value=0.0, max_value=1.0, step=0.01),
    "oxford_efficacy_infection": Slider("Eficácia Oxford (Infecção)", value=0.60, min_value=0.0, max_value=1.0, step=0.01),
    "pfizer_efficacy_progression": Slider("Eficácia Pfizer (Progressão)", value=0.90, min_value=0.0, max_value=1.0, step=0.01),
    "oxford_efficacy_progression": Slider("Eficácia Oxford (Progressão)", value=0.75, min_value=0.0, max_value=1.0, step=0.01),
}

server = ModularServer(
    VirusModel,
    [network, chart],
    "Modelo SEIRD no Virus on a Network",
    model_params,
)

server.port = 8521
server.launch()