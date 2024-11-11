import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean
import networkx as nx


class DistanceStrategy:
    """Strategy for calculating distance between neighborhoods using Euclidean Distance.

    This class implements a static method to compute distances between vectors
    representing neighborhood attributes.
    """

    @staticmethod
    def calculate(vector1, vector2):
        """Calculates the Euclidean distance between two vectors.

        Args:
            vector1 (array-like): First vector of attributes.
            vector2 (array-like): Second vector of attributes.

        Returns:
            float: The Euclidean distance between the vectors.
        """
        return euclidean(vector1, vector2)


class LayerFactory:
    """Factory for building layers of the multiplex network.

    Generates a layer where links between neighborhoods are based on a distance
    metric and are created only if they meet the connection threshold.

    Attributes:
        distance_strategy: Strategy object for calculating distances.
        threshold (float): Maximum distance threshold for creating connections.
    """

    def __init__(self, distance_strategy, threshold):
        self.distance_strategy = distance_strategy
        self.threshold = threshold

    def create_layer(self, barrios_data, attribute_column):
        """Creates a network layer based on the specified attribute.

        Args:
            barrios_data (pd.DataFrame): DataFrame containing neighborhood data and attributes.
            attribute_column (str): Name of the attribute column for this layer.

        Returns:
            nx.Graph: Graph of the layer with weighted edges.
        """
        layer_graph = nx.Graph()

        for i, barrio_i in barrios_data.iterrows():
            for j, barrio_j in barrios_data.iterrows():
                if i < j:
                    distance = self.distance_strategy.calculate(
                        barrio_i[attribute_column],
                        barrio_j[attribute_column]
                    )

                    if distance <= self.threshold:
                        layer_graph.add_edge(
                            barrio_i['barrio_id'], barrio_j['barrio_id'], weight=1 / (1 + distance)
                        )

        return layer_graph


class MultiplexNetwork:
    """Main class that manages the multiplex network and its layers.

    This class handles the creation and management of multiple network layers,
    each representing different neighborhood attributes.

    Attributes:
        barrios_data (pd.DataFrame): DataFrame containing neighborhood data.
        layers (dict): Dictionary storing the network layers.
    """

    def __init__(self, barrios_data):
        self.barrios_data = barrios_data
        self.layers = {}

    def add_layer(self, attribute_column, distance_strategy, threshold):
        """Adds a layer to the multiplex network for a specific attribute.

        Args:
            attribute_column (str): Name of the attribute column.
            distance_strategy (DistanceStrategy): Strategy for calculating distances.
            threshold (float): Connection threshold.
        """
        layer_factory = LayerFactory(distance_strategy, threshold)
        layer_graph = layer_factory.create_layer(self.barrios_data, attribute_column)
        self.layers[attribute_column] = layer_graph

    def get_layer(self, attribute_column):
        """Retrieves a specific layer from the multiplex network.

        Args:
            attribute_column (str): Name of the attribute column.

        Returns:
            nx.Graph: The requested network layer, or None if not found.
        """
        return self.layers.get(attribute_column, None)

    def get_multiplex_layers(self):
        """Returns all layers in the multiplex network.

        Returns:
            dict: Dictionary containing all network layers.
        """
        return self.layers
