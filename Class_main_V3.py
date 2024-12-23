# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 21:24:33 2024

@author: nico2
"""

import geojson
import numpy as np
from math import radians, cos, sin, asin, sqrt
import heapq

class SkiResortAnalyzer:
    def __init__(self):
        pass
    
    def haversine(self, lat1, lon1, lat2, lon2):
        """
        Calcule la distance entre deux points géographiques en utilisant la formule de Haversine.

        Parameters:
        lat1 (float): Latitude du premier point.
        lon1 (float): Longitude du premier point.
        lat2 (float): Latitude du deuxième point.
        lon2 (float): Longitude du deuxième point.

        Returns:
        float: Distance en kilomètres entre les deux points.
        """
        
        R = 6372.8  
        dLat = radians(lat2 - lat1)
        dLon = radians(lon2 - lon1)
        lat1 = radians(lat1)
        lat2 = radians(lat2)

        a = sin(dLat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dLon / 2) ** 2
        c = 2 * asin(sqrt(a))

        return R * c

    def getNodes(self, features):
        """
        Identifie les nœuds uniques à partir des données GeoJSON et leur attribue des IDs.

        Parameters:
        features (list): Liste des entités GeoJSON.

        Returns:
        dict: Dictionnaire des nœuds avec leurs IDs.
        """
        
        nodes = {}
        nodeId = 0
        epsilon = 0.0029
        
        for feature in features:
            properties = feature['properties']
            if 'aerialway' in properties or 'piste:type' in properties:
                if 'name' in properties or "piste:difficulty" in properties:
                    start_lat = feature['geometry']['coordinates'][0][1]
                    start_lon = feature['geometry']['coordinates'][0][0]
                    node_start = (start_lat, start_lon)
                    
                    verif_start = False
                    for lat, lon in nodes.keys():
                        if np.abs(lat - start_lat) < epsilon and np.abs(lon - start_lon) < epsilon:
                            verif_start = True
                            break
                    if not verif_start:
                        nodes[node_start] = nodeId
                        nodeId += 1
    
                    end_lat = feature['geometry']['coordinates'][-1][1]
                    end_lon = feature['geometry']['coordinates'][-1][0]
                    node_end = (end_lat, end_lon)
                    
                    verif_end = False
                    for lat, lon in nodes.keys():
                        if np.abs(lat - end_lat) < epsilon and np.abs(lon - end_lon) < epsilon:
                            verif_end = True
                            break
                    if not verif_end:
                        nodes[node_end] = nodeId
                        nodeId += 1
        return nodes

    def test_geojson(self, filename):
        """
        Analyse un fichier GeoJSON pour créer un graphe des téléphériques et pistes.

        Parameters:
        filename (str): Chemin du fichier GeoJSON.

        Returns:
        tuple: Matrice d'adjacence du graphe, détails des chemins, et dictionnaire des nœuds.
        """
        
        epsilon = 0.0029
        with open(filename, 'r', encoding="utf-8") as file:
            geojson_data = geojson.load(file)

        nodes = self.getNodes(geojson_data['features'])
        paths = []
        compteur = 0

        for feature in geojson_data['features']:
            properties = feature['properties']
            if ('aerialway' in properties or 'piste:type' in properties) and 'name' in properties or "piste:difficulty" in properties:
                start_lat = feature['geometry']['coordinates'][0][1]
                start_lon = feature['geometry']['coordinates'][0][0]
                end_lat = feature['geometry']['coordinates'][-1][1]
                end_lon = feature['geometry']['coordinates'][-1][0]

                nodeStartId = None
                nodeEndId = None

                for coord in nodes.keys():
                    lat_noeud = coord[0]
                    lon_noeud = coord[1]
                    if np.abs(lat_noeud - start_lat) < epsilon and np.abs(lon_noeud - start_lon) < epsilon:
                        nodeStartId = nodes.get(coord)
                    if np.abs(lat_noeud - end_lat) < epsilon and np.abs(lon_noeud - end_lon) < epsilon:
                        nodeEndId = nodes.get(coord)
                
                if nodeStartId is not None and nodeEndId is not None:
                    dist = int(self.haversine(start_lat, start_lon, end_lat, end_lon) * 1000)
                    if 'name' not in properties:
                        description = "liaison"
                    else:
                        description = properties['name']
                    record = {
                        'start': nodeStartId,
                        'end': nodeEndId,
                        'dist': dist,
                        'type': "lift" if 'aerialway' in properties else "piste",
                        'description': description,
                        'coordonees': feature['geometry']['coordinates']
                    }
                    paths.append(record)
                compteur += 1

        graph = np.zeros((len(nodes), len(nodes)), dtype=int)
        for path in paths:
            start = path['start']
            end = path['end']
            graph[start, end] = path['dist']

        return graph, paths, nodes
        
    def dijkstra(self, graph, start_node):
        """
        Trouve les plus courts chemins depuis un nœud de départ dans un graphe pondéré.

        Parameters:
        graph (numpy.ndarray): Matrice d'adjacence du graphe.
        start_node (int): Nœud de départ.

        Returns:
        tuple: Distances minimales et prédécesseurs pour chaque nœud.
        """
        
        n = graph.shape[0]
        distances = [float('inf')] * n
        distances[start_node] = 0
        predecessors = [-1] * n
        priority_queue = [(0, start_node)]
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            if current_distance > distances[current_node]:
                continue

            for neighbor in range(n):
                distance = graph[current_node, neighbor]
                if distance > 0:
                    new_distance = current_distance + distance
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        predecessors[neighbor] = current_node
                        heapq.heappush(priority_queue, (new_distance, neighbor))
        
        return distances, predecessors

    def get_path_dijkstra(self, Pr, i, j):
        """
        Reconstruit le chemin de i à j en utilisant la matrice des prédécesseurs.

        Parameters:
        Pr (list): Liste des prédécesseurs.
        i (int): Nœud de départ.
        j (int): Nœud d'arrivée.

        Returns:
        list: Chemin du nœud de départ au nœud d'arrivée.
        """
    
        path = []
        noeud_actuelle = j
        while noeud_actuelle != -1:
            path.append(noeud_actuelle)
            if noeud_actuelle == i:
                break
            noeud_actuelle = Pr[noeud_actuelle]
        return path[::-1]

    def show_path(self, paths, Pr, i, j):
        """
        Affiche les détails des pistes et téléphériques pour atteindre le nœud d'arrivée.

        Parameters:
        paths (list): Liste des chemins.
        Pr (list): Liste des prédécesseurs.
        i (int): Nœud de départ.
        j (int): Nœud d'arrivée.

        Returns:
        tuple: Chemin et liste des pistes/téléphériques à emprunter.
        """
        
        path = self.get_path_dijkstra(Pr, i, j)
        list_path = []
        if len(path) > 1:
            for values in range(len(path) - 1):
                a = path[values]
                b = path[values + 1]

                for record in paths:
                    if record['start'] == a and record['end'] == b:
                        chain = record['type'] + ' ' + record['description']
                        list_path.append(chain)
        else:
            for record in paths:
                if record['start'] == i and record['end'] == j:
                    chain = record['type'] + ' ' + record['description']
                    list_path.append(chain)
        return path, list_path
