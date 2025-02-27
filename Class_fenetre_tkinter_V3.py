# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 16:25:42 2024

@author: nico2
"""


import os
import tkinter as tk
import tkintermapview
from tkinter import scrolledtext
from PIL import Image, ImageTk
from Class_main_V3 import SkiResortAnalyzer


class FenetreGraphique:
    
    def __init__(self, root):
        """
        Initialise la fenêtre principale et affiche un écran de chargement avant de montrer l'application.
        
        :param root: La fenêtre principale de l'application Tkinter.
        """
        
        self.root = root
        self.root.title("SKI NAV")
        self.root.withdraw()
        self.coordonnees = {}
        self.click_count = 0
        self.ligne_trace = []
        self.create_loading_screen()
        self.analyzer = SkiResortAnalyzer()
        self.graph, self.paths, self.nodes = self.analyzer.test_geojson("Ski-Areas/chamrousse.geojson")
        self.root.after(3000, self.show_main_window)
        
        
    def create_loading_screen(self):
        """
        Affiche une fenêtre de chargement avec une image et un message.
        """
        
        self.loading_screen = tk.Toplevel()
        self.loading_screen.title("Loading...")

        image = Image.open("loading_image.jpg")
        image.save("loading_image.png")
        self.loading_image = tk.PhotoImage(file="loading_image.png")

        loading_image_label = tk.Label(self.loading_screen, image=self.loading_image)
        loading_image_label.grid(row=0, column=0, padx=20, pady=20)

        loading_label = tk.Label(self.loading_screen, text="Loading...", font=("Helvetica", 18))
        loading_label.grid(row=1, column=0, padx=20, pady=20)


    def show_main_window(self):
        """
        Détruit l'écran de chargement et affiche la fenêtre principale de l'application.
        """
        
        self.loading_screen.destroy()
        self.root.deiconify()
        self.create_main_window()


    def create_main_window(self):
        """
        Configure la fenêtre principale avec une carte interactive, des marqueurs et des éléments d'interface utilisateur.
        """
        
        self.map_widget = tkintermapview.TkinterMapView(self.root, width=2350, height=700, corner_radius=0)
        self.map_widget.grid(row=0, column=4, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        current_path = os.path.dirname(os.path.abspath(__file__))
        self.pin_image = ImageTk.PhotoImage(Image.open(os.path.join(current_path, "pin.png")).resize((16, 16)))
        
        for coord, id_noeud in self.nodes.items(): 
            lat = coord[0]
            lon = coord[1]
            self.map_widget.set_marker(lat, lon, text=str(id_noeud), icon=self.pin_image, command=self.marker_callback)
            self.coordonnees[id_noeud] = (lat, lon)

        self.map_widget.set_position(45.1255485, 5.9022395)
        self.map_widget.set_zoom(14)

        self.left_frame = tk.Frame(self.root)
        self.left_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.root.columnconfigure(1, weight=3)

        font_style = ("Helvetica", 18, "bold")
        text_label1 = tk.Label(self.left_frame, text="Point de départ :", font=font_style)
        text_label1.grid(row=0, column=0, sticky="w")
        self.entry1 = tk.Entry(self.left_frame, font = ("Helvetica", 15, "bold"))
        self.entry1.grid(row=1, column=0, sticky="ew", ipady = 20)

        text_label2 = tk.Label(self.left_frame, text="Point d'arrivée:", font=font_style)
        text_label2.grid(row=2, column=0, sticky="w")
        self.entry2 = tk.Entry(self.left_frame, font = ("Helvetica", 15, "bold"))
        self.entry2.grid(row=3, column=0, sticky="ew", ipady = 20)

        afficher_button = tk.Button(self.left_frame, text="Afficher", command=self.afficher_texte, height = 3, font =("Helvetica", 15, "bold"))
        afficher_button.grid(row=4, column=0, sticky="ew")
        
        self.scrolled_text = scrolledtext.ScrolledText(self.left_frame, wrap=tk.WORD, width=40, height=35, font = ("Helvetica", 10))
        self.scrolled_text.grid(row=6, column=0, sticky="ew", pady=5)
        
        clear_button = tk.Button(self.left_frame, text="Effacer les trajets précédents", command=self.effacer_lignes, height = 3, font =("Helvetica", 15, "bold"))
        clear_button.grid(row=5, column=0, columnspan=2, sticky="ew")
        
        text = tk.Label(self.left_frame, text="Les télésièges sont en rouge et les pistes sont en bleu", font=("Helvetica", 10, "bold"))
        text.grid(row=8, column=0, sticky="w")


    def marker_callback(self, marker):   
        """
        Met à jour les champs d'entrée avec les identifiants des marqueurs cliqués.

        :param marker: Le marqueur cliqué sur la carte.
        """
        
        marker_text = marker.text
        if self.click_count == 0:
            self.entry1.delete(0, tk.END)
            self.entry1.insert(0, marker_text)
            self.click_count += 1
        elif self.click_count == 1:
            self.entry2.delete(0, tk.END)
            self.entry2.insert(0, marker_text)
            self.click_count += 1
        
        
    def tracer_ligne(self, chemin_indice, piste):
        """
        Trace des lignes sur la carte entre les points spécifiés par le chemin.

        :param chemin_indice: Liste d'identifiants de points représentant le chemin.
        :param piste: Liste des types de chemin (lift ou piste).
        """
        
        for i in range(len(chemin_indice) - 1): 
            coord1 = self.coordonnees[chemin_indice[i]]
            coord2 = self.coordonnees[chemin_indice[i + 1]]
            for path in self.paths:
                if path['start'] == chemin_indice[i] and path['end'] == chemin_indice[i + 1]: 
                    coordonnees = path['coordonees']
                    break
            if 'lift' in piste[i]: 
                ligne = self.map_widget.set_path([coord1, coord2], color="red")
                self.ligne_trace.append(ligne)
            else: 
                ligne = self.map_widget.set_path([coord1, (coordonnees[0][1], coordonnees[0][0])], color="blue")
                self.ligne_trace.append(ligne)
                for i in range(len(coordonnees) - 1): 
                    lat1 = coordonnees[i][0]
                    lon1 = coordonnees[i][1]
                    lat2 = coordonnees[i + 1][0]
                    lon2 = coordonnees[i + 1][1]
                    ligne = self.map_widget.set_path([(lon1, lat1), (lon2, lat2)], color="blue")
                    self.ligne_trace.append(ligne)
                ligne = self.map_widget.set_path([(lon2, lat2), coord2], color="blue")
                self.ligne_trace.append(ligne)
        
        
    def afficher_texte(self):
        """
        Affiche les instructions de navigation et trace le chemin sur la carte.
        """
        
        self.entry1_value = self.entry1.get().strip()
        self.entry2_value = self.entry2.get().strip()
        
        if self.entry1_value and self.entry2_value: 
            try:
                self.entry1_int = int(self.entry1_value)
                self.entry2_int = int(self.entry2_value)
                D, Pr = self.analyzer.dijkstra(self.graph, self.entry1_int) # Pr est une matrice avec la distance entre le noeud i a j, et D correspond a la distance entre le neud i a j
                chemin_indice, chemin_nom_piste = self.analyzer.show_path(self.paths, Pr, self.entry1_int, self.entry2_int)
                self.scrolled_text.insert(tk.INSERT, f"Voici les pistes et remontées à emprunter pour vous rendre au point {self.entry2_int} : ")
                for piste in chemin_nom_piste: 
                    self.scrolled_text.insert(tk.INSERT, f"{piste} \n")
                self.scrolled_text.insert(tk.INSERT, '\n')
                self.tracer_ligne(chemin_indice, chemin_nom_piste)
            except ValueError:
                self.scrolled_text.insert(tk.INSERT, text="Les valeurs doivent être des nombres entiers.")
        else:
            self.scrolled_text.insert(tk.INSERT, text="Veuillez entrer des valeurs dans les deux champs.")
        self.click_count = 0
        
        
    def effacer_lignes(self):  
        """
        Efface toutes les lignes tracées et réinitialise le champ de texte.
        """
        
        for ligne in self.ligne_trace:
            self.map_widget.delete(ligne)
        self.ligne_trace.clear()
        self.scrolled_text.delete('1.0', tk.END)
    
    
if __name__ == '__main__':
    root = tk.Tk()
    app = FenetreGraphique(root)
    root.mainloop()