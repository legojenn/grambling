# Title:          Roulette Number Predictor for Play Like a Pro/Fibonacci Dozens
# Version:        2.0.1
# Started:        2024-01-22
# Last Modified:  2024-01-26
# Python version: 3.10.12
# Pandas version: 2.1.4
# Purpose:        Reads input from keyboard for last value spun in roulette
#                 and number of spins since the bet won, max number of spins
#                 between wins and median number of spins.
#
# Note:           Code was rewritten to optimise processing 
temp=[]
# Import Pandas & NumPy
import pandas as pd
import numpy  as np
# Import from OS 
from os import system, name

# Load series of roulette numbers
series = pd.read_csv("roulette_series.csv")

# Create lists to save winning numbers 
# and variables to count losses
series_names = series.columns.tolist()
wins   = {}
losses = {}
for series_name in series_names:
    key = str(series_name)
    losses[key] = 0
    wins[key] = []

def print_settings(threshold_1_to_1_print, threshold_2_to_1_print, exclude_below_threshold_print):
    print("Betting thresholds: " + str(threshold_1_to_1_print) + " for one to one bets and " + str(threshold_2_to_1_print) + " for two to one bets")
    if(exclude_below_threshold_print):
        print("Excluding", end = "")
    else:
        print("Including", end = "")
    print(" values below the betting threshold in percentiles.\n")

def print_results_table(series_names,calc_percentile_results,threshold_1, threshold_2):
    print('{0: <15}'.format(''), end = "")
    print('{0: <13}'.format('Spins Since'), end = "")
    print('{0: <15}'.format('Maximum Spins'), end = "")
    print('{0: <7}'.format(''), end = "")
    print('{0: <15}'.format('   ' + str(calc_percentile_results) + 'th'), end = "")
    print('{0: <10}'.format(''))

    print('{0: <15}'.format('Bet'), end = "")
    print('{0: <13}'.format(' Last Hit'), end = "")
    print('{0: <15}'.format('Between Hits'), end = "")
    print('{0: <7}'.format('Hits'), end = "")
    print('{0: <15}'.format('Percentile'), end="")
    print('{0: <10}'.format('Threshold'))
    print("⎼" * 80)
    for series_name in series_names:
        if (len(wins[series_name]) > 0):
            if (series[series_name].count() > 12):
                threshold = threshold_1
            else:
                threshold = threshold_2
            print('{0: <15}'.format(series_name), end = "")
            print('{0: >7}'.format(losses[series_name]), end = "")
            print('{0: >14}'.format(max(wins[series_name])), end = "")
            print('{0: >11}'.format(len(wins[series_name])), end = "")
            temp_list = wins[series_name]
            temp_list = [x for x in temp_list if x >= threshold]
            if(len(temp_list) > 0):        
                temp = float("{:.1f}".format(np.percentile(temp_list, calc_percentile_results)))
                print('{0: >10}'.format(str(temp)), end = "")
            else:
                print('{0: >10}'.format("N/A"), end = "")
            print('{0: >13}'.format(threshold), end = "")
            print("")
            print("-" * 80)


def print_suggested_bets(series_names,calc_percentile,threshold_1, threshold_2, max_difference):

    print("\nBets at or over threshold:")
    for series_name in series_names:
        if (series[series_name].count() > 12):
            threshold = threshold_1
        else:
            threshold = threshold_2
        if (len(wins[series_name]) > 0):
            if ((losses[series_name] >= threshold)):
                print(" " + str(series_name), end = "")
    print(" ")

    print("\nBets over threshold within " + str(max_difference)  + " losses of maximum:")
    for series_name in series_names:
        if (series[series_name].count() > 12):
            threshold = threshold_1
        else:
            threshold = threshold_2
        if (len(wins[series_name]) > 0):
            if ((max(wins[series_name]) < losses[series_name] + max_difference) and (losses[series_name] >= threshold)):
                print(" " + str(series_name), end = "")
    print(" ")

    print("\nBets over threshold and in the " + str(calc_percentile) + "th percentile:")
    for series_name in series_names:
        if (series[series_name].count() > 12):
            threshold = threshold_1
        else:
            threshold = threshold_2
        if (len(wins[series_name]) > 0):
            temp_list = wins[series_name]
            temp_list = [x for x in temp_list if x >= threshold]
            if(len(temp_list) > 0):
                if (losses[series_name] >= np.percentile(temp_list, calc_percentile)):     
                    print(" " + str(series_name), end = "")
    print(" ")


def main():
    # Set global variables
    current_number          = 0
    max_difference          = 2
    threshold_1_to_1        = 4
    threshold_2_to_1        = 9
    exclude_below_threshold = True
    if (exclude_below_threshold == False):
        threshold_1_to_1    = 0
        threshold_2_to_1    = 0
    calc_percentile         = 60

    # Core Loop
    # Collect spin value- fix it to account for errors
    while (current_number != 99):
        print('—' * 80)
        current_number = int(input("Enter the last spin (99 to quit): "))
        print('—' * 80)
        if(current_number != 99):
            # Check number against group lists
            # check_values(current_number,series_names) function does not work
            for series_name in series_names:
                if (current_number in series[series_name].values):
                    wins[series_name].append(losses[series_name])
                    losses[series_name] = 0
                else: 
                    losses[series_name] += 1

            #Print statistics
            print_results_table(series_names,calc_percentile,threshold_1_to_1, threshold_2_to_1)
            #Print suggestions
            print_suggested_bets(series_names,calc_percentile,threshold_1_to_1, threshold_2_to_1, max_difference)

if __name__ == "__main__":
    main()