
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 15:51:20 2025

@author: bouchet
"""

###############################################################################
#                                 IMPORTS                                     #
###############################################################################

import preprocessing as pp

import visualisation as vi
from descriptive_analysis import from_stack_to_number_of_interaction_sequences,from_distance_to_sequences_vector, from_distances_to_sequences_stack,from_seq_to_average_interaction_time,from_seq_to_daily_interactions

import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt

import dotenv
import sys
import time
from env_loading import parent_dir, output_dir

if os.getcwd().endswith("TRACE_module"):
    new_path = os.getcwd()[:-len("TRACE_module")] + "UTILS_module"
elif os.getcwd().endswith("TRACE_IODAA"):
    new_path = os.getcwd() + os.sep + "UTILS_module"
sys.path.insert(0, new_path) # insert path to be able to import file afterwards, allows for imports wherever the script is called from

from UTILS_files import test_import
if test_import() : # Testing the import
    from UTILS_files import get_all_files_within_one_folder # Importing the wanted function
else :
    print("Import failed")



import preprocessing as pp



###############################################################################
#                                 SCRIPTS                                     #
###############################################################################

folder= parent_dir
list_files=list()

##################################
#ETAPE 1 - Obtention des fichiers#
##################################


t1=time.perf_counter()

list_files = get_all_files_within_one_folder(folder, True, extension=".parquet")

t2=time.perf_counter()
######################################
#ETAPE 2 - Concaténation des fichiers#
######################################


folder_savings =  os.sep.join([output_dir,"savings"])
if not  os.path.isdir(folder_savings) :
    os.makedirs(folder_savings)

data=pp.concatenate_df(list_files)

##########################################
#ETAPE 3 -Transformation RSSI en distance#
##########################################
t3=time.perf_counter()

#data=pp.transform_rssi_to_distance(data)
t4=time.perf_counter()

###################################################################
#ETAPE 5 - Création d'un stack de matrice d'adjacence symétriques #
###################################################################

list_id=list(pd.unique(data["accelero_id"]))


stack,list_timesteps=pp.create_stack(data,list_id)
t5=time.perf_counter()

###################################################################
#ETAPE 6- Analyses                                                #
###################################################################


#start_time = pd.Timestamp('2024-03-20T08:39:00.000000000')
#end_time = pd.Timestamp('2024-04-10T16:36:00.000000000')

start_time = pd.Timestamp('2024-03-22T08:39:00.000000000')
end_time = pd.Timestamp('2024-04-8T16:36:00.000000000')


stack,list_timesteps=pp.crop_start_end_stack(stack=stack,
                         list_timesteps = list_timesteps ,
                         start = start_time,
                         end = end_time)

###

distances_clean=stack
t5b=time.perf_counter()
#####
#print(distances_clean[0 ,:, : ])
print(distances_clean.shape)

distances_clean=np.where(distances_clean==0,np.nan,distances_clean)
## Creation a a sequence matrix
matrice_seq = from_distances_to_sequences_stack(distances_clean)

###

number_of_interaction_sequences = from_stack_to_number_of_interaction_sequences(matrice_seq)


number_of_daily_interaction = from_seq_to_daily_interactions(matrice_seq,list_timesteps)
average_duration_of_an_interaction = from_seq_to_average_interaction_time(matrice_seq)

t6=time.perf_counter()

#####################
#Visualisation#
#####################


vi.heatmap_interactions_number(number_of_interaction_sequences,list_id)


## PLotting the double boxplot :

# Create the figure and axis
vi.barplot_interaction_cows(number_of_daily_interaction,average_duration_of_an_interaction ,list_id)

print("--BENCHMArk-- \n ==========\n étape 1 - localisation des données: {} \n étape 2 - concaténation des fichiers et création d'un dataframe unique ': {} \n étape 3 -transformation des signaux RSSI en distance {} \n étape 4 - Mise en forme des données sous forme matricielle: {} \n étape 5 : Analyse descriptive :{} ".format(t2-t1,t3-t2,t4-t3,t5-t4,t6-t5))

vi.boxplot_average_time_number_interactions(number_of_daily_interaction,
                                             average_duration_of_an_interaction)
