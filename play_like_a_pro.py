# Title:          Roulette Number Predictor
# Version:        0.3.1
# Started:        2024-01-22
# Last Modified:  2024-03-02
# Python version: 3.10.12
# Pandas version: 2.1.4
# NumPy version:  X
# Purpose:        Reads input from keyboard for last value spun in roulette
#                 and number of spins since the bet won, max number of spins
#                 between wins and median number of spins.
#
# Note:           Code was rewritten to optimise processing 
# To-do:          1) Move as much functionality as possible into functions
#                 2) Permit on the fly changes threshold & percentile 
#                    and store in config file.
#                 3) Migrate to GUI

# Import Pandas & NumPy
import pandas as pd
import numpy  as np
from scipy.stats import chi2
# Import from OS
import os
from os import name
# Import Text colour
import colorama
colorama.init()
# Load series of roulette numbers
series = pd.read_csv("roulette_series.csv")
# Removes columns with ! as first character (keep but don't use)
series.drop(series.columns[series.columns.str.contains('^X')], axis=1)
# CONSTANTS
SCREEN_WIDTH       = 86
NUMBERS_TO_DISPLAY = 16
NUMBERS_ON_WHEEL   = 37
ARROW_UP           = "↑"
ARROW_DOWN         = "↓"
ARROW_SAME         = "-"
#———————————————————————————————————————————————————————————————————————————————
# Clear screen
def clear():
    # for windows
    if name == 'nt':
        os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        os.system('clear')
#———————————————————————————————————————————————————————————————————————————————
#Print default settings
def print_settings(i_threshold_1_to_1, i_threshold_2_to_1, i_threshold_3):
    print(f"\nInitial betting thresholds: {i_threshold_1_to_1} for one to one bets;")
    print(f"                            {i_threshold_2_to_1} for two to one bets; and")
    print(f"                            {i_threshold_3} for 2 dozens or columns. \n")
#———————————————————————————————————————————————————————————————————————————————
def print_horizontal_line(s_symbol):
    match s_symbol:
        case "L":
            s_line_char = "—"
        case "M":
            s_line_char = "-"
        case "S":
            s_line_char = "⋅"
        case _:
            s_line_char = "~"
    print(s_line_char * SCREEN_WIDTH)

def test_randomness(data):
    observed_frequencies, _ = np.histogram(data, bins=10)  # Adjust number of bins as needed
    expected_frequency = len(data) / 10  # Expected frequency for each bin assuming uniform distribution
    chi_squared_statistic = np.sum((observed_frequencies - expected_frequency)**2 / expected_frequency)
    degrees_of_freedom = len(observed_frequencies) - 1
    critical_value = chi2.ppf(0.95, degrees_of_freedom)  # Significance level 0.05
    p_value = 1 - chi2.cdf(chi_squared_statistic, degrees_of_freedom)
    
    if chi_squared_statistic > critical_value:
        return "Data is not likely random."
    else:
        return "Data is likely random."
#———————————————————————————————————————————————————————————————————————————————
# Print last numbers up to x most recent numbers spun on the roulette wheel
def recent_numbers(l_winners, i_num_played):
    if (len(l_winners) < NUMBERS_TO_DISPLAY):
        i_num_display = len(l_winners)
    else:
        i_num_display = NUMBERS_TO_DISPLAY
    print(f"Spins: {len(l_winners)}")
    if (i_num_played == 1):
        print(f"Last number: ", end = "")
    else:
        print(f"Last {i_num_display} numbers:", end = "")


    for i_temp_loop in range(0,i_num_display):
        print("⎹", end="")
        print(colorama.Back.RESET, end ="")
        if(l_winners[(i_temp_loop)] in series['Red'].values):
            print(colorama.Back.RED, end ="")
        elif(l_winners[(i_temp_loop)] in series['Black'].values):
            print(colorama.Back.BLACK, end ="")
        else:
            print(colorama.Back.GREEN + colorama.Fore.WHITE, end ="")
        print("⎸", end="")
        print(colorama.Fore.WHITE + colorama.Style.BRIGHT + '{0: >2}'.format(l_winners[(i_temp_loop)]), end = "")
    print("⎹", end="")
    print (colorama.Back.RESET + colorama.Fore.RESET + colorama.Style.RESET_ALL, end="")
    print("⎸")
    if(i_num_played >= 50):
        print_horizontal_line("M")
        result = test_randomness(l_winners)
        print(result)
    print_horizontal_line("L")
    return len(l_winners)
#———————————————————————————————————————————————————————————————————————————————
# Reads input from keyboard. If value entered is an integer, between 0 and 36
# or 99, otherwise request input again.

def get_spin():
    b_valid = False
    while (not b_valid):
        s_current_number = str(input("Enter the last spin (99 to quit): "))
        if(s_current_number.isdigit()):
            i_current_number = int(s_current_number)
            if((0 <= i_current_number <= 36) or i_current_number == 99):
                b_valid = True
            else:
                print("Error! The value entered must be an integer between 0 and 36.\n")
        else:
            print("Error! The value entered must be an integer between 0 and 36.\n")
    return i_current_number
#———————————————————————————————————————————————————————————————————————————————
def print_results_table(l_series_names,i_threshold_1_to_1, i_threshold_2_to_1, i_threshold_2_doz_or_col, d_wins, l_losses, i_spins):
    i_temp_loop = 0
    print('{0: ^23}'.format(''), end = "")
    print('{0: ^11}'.format('Spins Since'), end = "")
    print('{0: ^13}'.format('Max Spins'), end = "")
    print('{0: ^11}'.format('Hits'), end = "")
    print('{0: ^11}'.format('Hit'))

    print('{0: <12}'.format('Bet'), end = "")
    print('{0: ^11}'.format('Threshold'), end = "")
    print('{0: ^11}'.format('Last Hit'), end = "")
    print('{0: ^13}'.format('Between Hits'), end = "")
    print('{0: ^11}'.format('>=Thld'), end = "")
    print('{0: ^11}'.format('Percent'), end="")
    print('{0: ^9}'.format('Mean'), end="")    
    print('{0: ^9}'.format('Std Dev'))
    print_horizontal_line("M")
    for series_name in l_series_names:
        #Calculate mean number and standard deviation for spins to win
        my_list  = d_wins[series_name]
        my_array = np.array(my_list)
        my_array = my_array +1
        f_mean   = float("{:.1f}".format(np.mean(my_array, axis=0)))
        f_std    = float("{:.1f}".format(np.nanstd(my_array, axis=0)))

        # choose threshold if minumum number of wins not met
        if (len(d_wins[series_name]) > 0):
            if (series[series_name].count() > 18):
                i_threshold = i_threshold_2_doz_or_col
            elif (series[series_name].count() > 12):
                i_threshold = i_threshold_1_to_1
            else:
                i_threshold = i_threshold_2_to_1

            #choose dynamic threshold of mean + 1 std for all trigger sthat dont start with -

            if (len(d_wins[series_name]) > 5 and series_name[0] != "-"):
                i_threshold = f_mean + f_std

            #set colours, yellow > mean; cyan > mean + 1 std; green > mean + 2 std 

            if (l_losses[series_name] >= f_mean and series_name[0] != "-" ):
                print(colorama.Fore.BLACK + colorama.Style.BRIGHT + colorama.Back.YELLOW, end = "")

            if (l_losses[series_name] >= i_threshold and series_name[0] != "-" ):
                print(colorama.Fore.WHITE + colorama.Style.BRIGHT + colorama.Back.CYAN, end = "")

            if (l_losses[series_name] >= (i_threshold + f_std)  and series_name[0] != "-" ):
                print(colorama.Fore.WHITE + colorama.Style.BRIGHT + colorama.Back.GREEN, end = "")

            # print trigger name

            print('{0: <15}'.format(series_name), end = "")
            
            # print threshold (mean + 1 std)

            i_threshold = float("{:.1f}".format(i_threshold))
            if (series_name[0] != "-"):          
                print('{0: >5}'.format(i_threshold), end = "")
            else:
                print('{0: >5}'.format("N/A"), end = "")

            # print spins since last win

            print('{0: >10}'.format(l_losses[series_name]), end = "")

            #print most spins between wins

            print('{0: >12}'.format(max(d_wins[series_name])), end = "")

            #print wins greater than the threshold

            temp_list = d_wins[series_name]
            temp_list = [ele for ele in temp_list if float(ele) >= i_threshold]
            if (series_name[0] != "-"):          
                print('{0: >12}'.format(len(temp_list)), end = "")
            else:
                print('{0: >12}'.format("N/A"), end = "")
            # print win percentage
            
            l_temp_list = d_wins[series_name]
            l_temp_list = [ele for ele in l_temp_list if float(ele) >= i_threshold]

            i_win_percent = float("{:.1f}".format(100 * (len(d_wins[series_name]) / i_spins)))


            i_expected_percent = series[series_name].count()/NUMBERS_ON_WHEEL

            if (i_win_percent > i_expected_percent*100):
                s_arrow = ARROW_UP
            elif(i_win_percent < i_expected_percent*100):
                s_arrow = ARROW_DOWN
            else:
                s_arrow = ARROW_SAME

            print('{0: >12}'.format(str(i_win_percent)+ s_arrow), end = "")  

            #print mean

            print('{0: >9}'.format(f_mean), end = "")

            # print standard deviation

            print('{0: >9}'.format(f_std), end = "")

            #reset colouring

            print (colorama.Back.RESET + colorama.Fore.RESET + colorama.Style.RESET_ALL, end="")
            print("")

            # add divider

            if (i_temp_loop % 3 == 2):
                print_horizontal_line("S")
            i_temp_loop += 1  

#———————————————————————————————————————————————————————————————————————————————
def main():
#————————————————————————————————————————
    # Set default 
    threshold_1_to_1        =  4 
    threshold_2_to_1        =  9
    threshold_2_doz_or_col  =  3 # basically all high coverage

    #try to put this in function
    current_number              =  0
    numbers_drawn               =  0
#————————————————————————————————————————
    # Create lists to save winning numbers 
    # and variables to count losses
    series_names = series.columns.tolist()
    wins            = {}
    losses          = {}
    for series_name in series_names:
        key = str(series_name)
        losses[key] = 0
        wins[key]   = []
    winning_numbers = []
#————————————————————————————————————————
    # Heading - Print initial settings
    print_settings(threshold_1_to_1, threshold_2_to_1, threshold_2_doz_or_col)
#————————————————————————————————————————
    # Core Loop
    # Collect spin value- fix it to account for errors
    while (current_number != 99):
        print_horizontal_line("L")

        # Collect spin value (or adjust global values (max_diff, percentile, threshold))
        current_number = get_spin()
        
        print_horizontal_line("L")
        
        if(current_number != 99):
            # Check number against group lists
            # Put this in function
            for series_name in series_names:
                if (current_number in series[series_name].values):
                    wins[series_name].append(losses[series_name])
                    losses[series_name] = 0
                else: 
                    losses[series_name] += 1
            numbers_drawn += 1
            winning_numbers.insert(0,current_number)
        
            #display last (x) winning_numbers
            spins = recent_numbers(winning_numbers, numbers_drawn)

            #Print statistics
            print_results_table(series_names, threshold_1_to_1, threshold_2_to_1, threshold_2_doz_or_col,  wins, losses, spins)
            
            #loop back again
if __name__ == "__main__":
    main()
