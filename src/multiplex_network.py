import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean
import networkx as nx


class DistanceStrategy:
    """Estrategia de cálculo de distancia entre barrios usando Distancia Euclidiana."""

    @staticmethod
    def calculate(vector1, vector2):
        return euclidean(vector1, vector2)


class LayerFactory:
    """
    Fábrica para construir capas de la red multiplex.
    Genera una capa donde los enlaces entre barrios están basados en una distancia.
    y se crean solo si cumplen con el umbral de conexión.
    """

    def __init__(self, distance_strategy, threshold):
        self.distance_strategy = distance_strategy
        self.threshold = threshold

    def create_layer(self, barrios_data, attribute_column):
        """
        Crea una capa de red basada en el atributo especificado.

        Args:
        - barrios_data (pd.DataFrame): DataFrame con los datos de los barrios y sus atributos.
        - attribute_column (str): Nombre de la columna del atributo para esta capa.

        Returns:
        - nx.Graph: Grafo de la capa con enlaces ponderados.
        """
        # Crear el grafo de la capa
        layer_graph = nx.Graph()

        # Iterar sobre pares de barrios
        for i, barrio_i in barrios_data.iterrows():
            for j, barrio_j in barrios_data.iterrows():
                if i < j:  # Evitar duplicados y la diagonal
                    # Calcular distancia entre los atributos de los dos barrios
                    distance = self.distance_strategy.calculate(
                        barrio_i[attribute_column],
                        barrio_j[attribute_column]
                    )

                    # Aplicar umbral de conexión
                    if distance <= self.threshold:
                        layer_graph.add_edge(
                            barrio_i['barrio_id'], barrio_j['barrio_id'], weight=1 / (1 + distance)
                        )

        return layer_graph


class MultiplexNetwork:
    """Clase principal que gestiona la red multiplex y sus capas."""

    def __init__(self, barrios_data):
        self.barrios_data = barrios_data
        self.layers = {}

    def add_layer(self, attribute_column, distance_strategy, threshold):
        """
        Añade una capa a la red multiplex para un atributo específico.

        Args:
        - attribute_column (str): Nombre de la columna del atributo.
        - distance_strategy (DistanceStrategy): Estrategia de cálculo de distancia.
        - threshold (float): Umbral de conexión.
        """
        layer_factory = LayerFactory(distance_strategy, threshold)
        layer_graph = layer_factory.create_layer(self.barrios_data, attribute_column)
        self.layers[attribute_column] = layer_graph

    def get_layer(self, attribute_column):
        """Obtiene una capa específica de la red multiplex."""
        return self.layers.get(attribute_column, None)

    def get_multiplex_layers(self):
        """Retorna todas las capas de la red multiplex."""
        return self.layers
