# Title:          Roulette Number Predictor
# Version:        2.0.3
# Started:        2024-01-22
# Last Modified:  2024-02-01
# Python version: 3.10.12
# Pandas version: 2.1.4
# NumPy version:  X
# Purpose:        Reads input from keyboard for last value spun in roulette
#                 and number of spins since the bet won, max number of spins
#                 between wins and median number of spins.
#
# Note:           Code was rewritten to optimise processing 
# To-do:          1) Fix function variables
#                 2) UPPER CASE constants
#                 3) Error correction
#                 5) Move as much functionality into funcions
#                 6) Permit on the fly changes threshold & percentile 
#                    and store in config file.
#                 7) Migrate to GUI

# Import Pandas & NumPy
import pandas as pd
import numpy  as np

# Import from OS
import os
from os import name

# Load series of roulette numbers
series = pd.read_csv("roulette_series.csv")

# Define our clear function
def clear():
    # for windows
    if name == 'nt':
        os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        os.system('clear')

def print_settings(threshold_1_to_1_print, threshold_2_to_1_print, threshold_3_print, exclude_below_threshold):
    print("Betting thresholds: " + str(threshold_1_to_1_print) + " for one to one bets, " + str(threshold_2_to_1_print) + " for two to one bets, and \n" + str(threshold_3_print) + " for 2 dozens or columns.")
    if(exclude_below_threshold):
        print("Excluding", end = "")
    else:
        print("Including", end = "")
    print(" values below the betting threshold in percentiles.\n")

def recent_numbers(winners, num_played, num_display):
    if (len(winners) < num_display):
        num_display = len(winners)
    print('Spins: ' + str(len(winners)))

    if (num_played == 1):
        print ('Last number: ', end = '')
    else:
        print ('Last ' + str(num_display) + ' numbers:')

    for temp_loop in range(0,num_display):
        print('{0: >3}'.format(winners[(temp_loop)]), end = "")
    print ('.')
    print('—' * 80)
    return len(winners)

def print_results_table(series_names,calc_percentile_results,threshold_1, threshold_2, threshold_3, exclude_below, wins, losses, spins):
    temp_loop = 0
    print('{0: <14}'.format(''), end = "")
    print('{0: <13}'.format('Spins Since'), end = "")
    print('{0: <14}'.format('Max Spins'), end = "")
    print('{0: <7}'.format('Hits'), end = "")
    if (exclude_below):
        excl_bel='E'
    else:
        excl_bel='I'
    exclude_string = str(calc_percentile_results) + 'th (' + excl_bel + ')'
    print('{0: <15}'.format(' ' + exclude_string), end = "")
    print('{0: <15}'.format('Hit'))

    print('{0: <15}'.format('Bet'), end = "")
    print('{0: <11}'.format('Last Hit'), end = "")
    print('{0: <15}'.format('Between Hits'), end = "")
    print('{0: <7}'.format('>=Thld'), end = "")
    print('{0: <12}'.format('Percentile'), end="")
    print('{0: <10}'.format('Percent'), end="")
    print('{0: <11}'.format('Threshold'))
    print("⎼" * 80)
    for series_name in series_names:
        if (len(wins[series_name]) > 0):
            if (series[series_name].count() > 18):
                threshold = threshold_3
            elif (series[series_name].count() > 12):
                threshold = threshold_1
            else:
                threshold = threshold_2
            print('{0: <15}'.format(series_name), end = "")
            print('{0: >5}'.format(losses[series_name]), end = "")
            print('{0: >13}'.format(max(wins[series_name])), end = "")
            temp_list = wins[series_name]
            temp_list = [ele for ele in temp_list if float(ele) >= threshold]            
            print('{0: >12}'.format(len(temp_list)), end = "")
            if(len(temp_list) > 0):        
                temp = float("{:.1f}".format(np.percentile(temp_list, calc_percentile_results)))
                print('{0: >10}'.format(str(temp)), end = "")
            else:
                print('{0: >10}'.format("N/A"), end = "")
            win_percent = float("{:.1f}".format(100 * (len(wins[series_name]) / spins)))
            print('{0: >12}'.format(str(win_percent)), end = "")    
            print('{0: >9}'.format(threshold), end = "")
            print("")
            if (temp_loop % 3 == 2):
                print("⋅" * 80)
            temp_loop += 1  

def print_suggested_bets(series_names,calc_percentile,threshold_1, threshold_2, threshold_3, max_difference, wins, losses):
    print("⎼" * 80)
    print("\nBets at or over threshold:")
    for series_name in series_names:
        if (series[series_name].count() > 18):
            threshold = threshold_3
        elif (series[series_name].count() > 12):
            threshold = threshold_1
        else:
            threshold = threshold_2
        if (len(wins[series_name]) > 0):
            if ((losses[series_name] >= threshold)):
                print(" " + str(series_name), end = "")
    print(" ")

    print("\nBets over threshold within " + str(max_difference)  + " losses of maximum:")
    for series_name in series_names:
        if (series[series_name].count() > 18):
            threshold = threshold_3
        elif (series[series_name].count() > 12):
            threshold = threshold_1
        else:
            threshold = threshold_2
        if (len(wins[series_name]) > 0):
            if ((max(wins[series_name]) < losses[series_name] + max_difference) and (losses[series_name] >= threshold)):
                print(" " + str(series_name), end = "")
    print(" ")

    print("\nBets over threshold and in the " + str(calc_percentile) + "th percentile:")
    for series_name in series_names:
        if (series[series_name].count() > 18):
            threshold = threshold_3
        elif (series[series_name].count() > 12):
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
#———————————————————————————————————————————————————————————————————————————————
def main():
    # Set global variables
    current_number              =  0
    max_difference              =  2
    threshold_1_to_1            =  4
    threshold_2_to_1            =  9
    threshold_2_doz_or_col      =  3
    exclude_below_threshold = True
    if (exclude_below_threshold == False):
        threshold_1_to_1        =  0
        threshold_2_to_1        =  0
        threshold_2_doz_or_col  =  0
    calc_percentile             = 60
    # Create lists to save winning numbers 
    # and variables to count losses
    series_names = series.columns.tolist()
    wins   = {}
    losses = {}
    initial_run = True
    for series_name in series_names:
        key = str(series_name)
        losses[key] = 0
        wins[key] = []
    winning_numbers = []
    numbers_drawn = 0
    numbers_to_display = 25
    print_settings(threshold_1_to_1, threshold_2_to_1, threshold_2_doz_or_col, exclude_below_threshold)
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
            numbers_drawn += 1
            winning_numbers.insert(0,current_number)
            
            #display last (x) winning_numbers
            spins = recent_numbers(winning_numbers, numbers_drawn, numbers_to_display)
            #Print statistics
            print_results_table(series_names, calc_percentile,threshold_1_to_1, threshold_2_to_1, threshold_2_doz_or_col, exclude_below_threshold, wins, losses, spins)
            #Print suggestions
            print_suggested_bets(series_names, calc_percentile,threshold_1_to_1, threshold_2_to_1, threshold_2_doz_or_col, max_difference, wins, losses)
if __name__ == "__main__":
    main()
