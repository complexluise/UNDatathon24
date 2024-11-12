import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from scipy.cluster.hierarchy import dendrogram, linkage, cut_tree
from scipy.spatial.distance import pdist
import plotly.figure_factory as ff


def load_and_prepare_data(file_path: str, separator: str = ';') -> pd.DataFrame:
    """
    Load and prepare the data from CSV file

    Args:
        file_path (str): Path to the CSV file
        separator (str): CSV separator character

    Returns:
        pd.DataFrame: Loaded and prepared dataframe
    """
    datos = pd.read_csv(file_path, sep=separator)
    print("Data loaded successfully!")
    print(f"Shape: {datos.shape}")
    return datos


def display_basic_info(datos: pd.DataFrame) -> None:
    """
    Display basic information about the dataset

    Args:
        datos (pd.DataFrame): Input dataframe
    """
    print("\nColumn names:", datos.columns)
    print("\nFirst few rows:")
    print(datos.head())
    print("\nData summary:")
    print(datos.describe())


def plot_distributions(datos: pd.DataFrame, variables: list) -> None:
    """
    Plot histograms for specified variables

    Args:
        datos (pd.DataFrame): Input dataframe
        variables (list): List of variables to plot
    """
    n_vars = len(variables)
    n_rows = (n_vars + 1) // 2  # Calculate number of rows needed

    fig, axes = plt.subplots(n_rows, 2, figsize=(12, 4 * n_rows))
    axes = axes.flatten()  # Flatten axes array for easier indexing

    for i, var in enumerate(variables):
        axes[i].hist(datos[var], color='blue', alpha=0.7)
        axes[i].set_title(f'{var} Distribution')
        axes[i].set_xlabel(var)
        axes[i].set_ylabel('Frequency')

    # Hide empty subplots if odd number of variables
    for i in range(n_vars, len(axes)):
        fig.delaxes(axes[i])

    plt.tight_layout()
    plt.show()


def create_correlation_matrix(datos: pd.DataFrame, exclude_cols: list = None) -> pd.DataFrame:
    """
    Create and plot correlation matrix

    Args:
        datos (pd.DataFrame): Input dataframe
        exclude_cols (list): Columns to exclude from correlation

    Returns:
        pd.DataFrame: Correlation matrix
    """
    if exclude_cols:
        km_data = datos.drop(exclude_cols, axis=1)
    else:
        km_data = datos

    correlation_matrix = km_data.corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix')
    plt.show()

    return correlation_matrix


def prepare_clustering_data(datos: pd.DataFrame, selected_vars: list) -> tuple:
    """
    Prepare data for clustering by selecting variables and scaling

    Args:
        datos (pd.DataFrame): Input dataframe
        selected_vars (list): Variables to use for clustering

    Returns:
        tuple: (Original selected data, Scaled data)
    """
    km = datos[selected_vars]
    scaler = StandardScaler()
    km_scale = scaler.fit_transform(km)
    km_scale = pd.DataFrame(km_scale, columns=selected_vars)

    return km, km_scale


def perform_kmeans(data: pd.DataFrame, n_clusters: int = 3, random_state: int = 42) -> tuple:
    """
    Perform K-means clustering

    Args:
        data (pd.DataFrame): Scaled data for clustering
        n_clusters (int): Number of clusters
        random_state (int): Random state for reproducibility

    Returns:
        tuple: (KMeans object, Cluster labels)
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    labels = kmeans.fit_predict(data)

    print("\nK-means Inertia:", kmeans.inertia_)
    print("\nCluster Centers:")
    centers_df = pd.DataFrame(kmeans.cluster_centers_, columns=data.columns)
    print(centers_df)

    return kmeans, labels


def plot_kmeans_results(datos: pd.DataFrame, labels: np.ndarray, variable: str) -> None:
    """
    Plot K-means clustering results

    Args:
        datos (pd.DataFrame): Original dataframe
        labels (np.ndarray): Cluster labels
        variable (str): Variable to plot
    """
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=labels, y=datos[variable])
    plt.title(f'{variable} Distribution by Cluster')
    plt.xlabel('Cluster')
    plt.show()


def perform_hierarchical(data: pd.DataFrame, n_clusters: int = 3) -> tuple:
    """
    Perform hierarchical clustering

    Args:
        data (pd.DataFrame): Scaled data for clustering
        n_clusters (int): Number of clusters

    Returns:
        tuple: (Linkage matrix, Cluster labels)
    """
    dist_matrix = pdist(data)
    linkage_matrix = linkage(dist_matrix, method='ward')

    plt.figure(figsize=(10, 7))
    dendrogram(linkage_matrix)
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('Sample Index')
    plt.ylabel('Distance')
    plt.show()

    hier_labels = cut_tree(linkage_matrix, n_clusters=n_clusters).flatten()

    return linkage_matrix, hier_labels


def perform_dbscan(data: pd.DataFrame, eps: float = 0.7, min_samples: int = 10) -> tuple:
    """
    Perform DBSCAN clustering

    Args:
        data (pd.DataFrame): Scaled data for clustering
        eps (float): Maximum distance between samples
        min_samples (int): Minimum number of samples in a neighborhood

    Returns:
        tuple: (DBSCAN object, Cluster labels)
    """
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(data)

    print("\nNumber of points in each DBSCAN cluster:")
    print(pd.Series(labels).value_counts().sort_index())

    return dbscan, labels


def plot_dbscan_results(data: pd.DataFrame, labels: np.ndarray, x_var: str, y_var: str) -> None:
    """
    Plot DBSCAN clustering results

    Args:
        data (pd.DataFrame): Scaled data
        labels (np.ndarray): Cluster labels
        x_var (str): Variable for x-axis
        y_var (str): Variable for y-axis
    """
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(data[x_var], data[y_var], c=labels, cmap='viridis')
    plt.title('DBSCAN Clustering Results')
    plt.xlabel(f'{x_var} (standardized)')
    plt.ylabel(f'{y_var} (standardized)')
    plt.colorbar(scatter)
    plt.show()


def calculate_cluster_summary(datos: pd.DataFrame, labels: np.ndarray,
                              selected_vars: list, cluster_name: str = 'Cluster') -> pd.DataFrame:
    """
    Calculate summary statistics for each cluster

    Args:
        datos (pd.DataFrame): Original dataframe
        labels (np.ndarray): Cluster labels
        selected_vars (list): Variables to summarize
        cluster_name (str): Name for the cluster column

    Returns:
        pd.DataFrame: Summary statistics by cluster
    """
    temp_df = datos.copy()
    temp_df[cluster_name] = labels
    summary = temp_df.groupby(cluster_name)[selected_vars].mean()
    print(f"\n{cluster_name} Summary Statistics:")
    print(summary)
    return summary


def main():
    """
    Main function to run the clustering analysis
    """
    # Load data
    datos = load_and_prepare_data('datos_curados.csv')  # TODO Change

    # Display basic information
    display_basic_info(datos)

    # Plot distributions
    variables_to_plot = ['tea', 't_sob', 't_form_te', 'Edad_prom'] # TODO Change
    plot_distributions(datos, variables_to_plot)

    # Create correlation matrix
    corr_matrix = create_correlation_matrix(datos, exclude_cols=['CodUPL', 'NombreUPL'])  # TODO Change

    # Prepare data for clustering
    selected_vars = ['tea', 't_sob', 'Edad_prom', 't_form_te']  # TODO Change
    km, km_scale = prepare_clustering_data(datos, selected_vars)

    # Perform K-means clustering
    kmeans, kmeans_labels = perform_kmeans(km_scale)
    plot_kmeans_results(datos, kmeans_labels, 'tea')
    kmeans_summary = calculate_cluster_summary(datos, kmeans_labels, selected_vars, 'K-means Cluster')

    # Perform hierarchical clustering
    linkage_matrix, hier_labels = perform_hierarchical(km_scale)
    hier_summary = calculate_cluster_summary(datos, hier_labels, selected_vars, 'Hierarchical Cluster')

    # Perform DBSCAN clustering
    dbscan, dbscan_labels = perform_dbscan(km_scale)
    plot_dbscan_results(km_scale, dbscan_labels, 'tea', 't_sob')  # TODO Change
    dbscan_summary = calculate_cluster_summary(datos, dbscan_labels, selected_vars, 'DBSCAN Cluster')

    return datos, kmeans_labels, hier_labels, dbscan_labels


if __name__ == "__main__":
    datos, kmeans_labels, hier_labels, dbscan_labels = main()