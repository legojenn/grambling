# Title:          Roulette Number Predictor
# Version:        0.3.8
# Started:        2024-01-22
# Last Modified:  2024-05-19
# Python version: 3.10.12
# Pandas version: 2.1.4
# NumPy version:  X
# Purpose:        Reads input from keyboard for last value spun in roulette
#                 and number of spins since the bet won, max number of spins
#                 between wins and median number of spins.
#
# Note:           Code was rewritten to optimise processing 
# To-do:          
#                 1) Option to remove last X spins, ie R5 deletes five
#                 2) Move as much functionality as possible into functions
#                 3) Migrate to GUI

# Import Pandas & NumPy
import pandas as pd
import numpy  as np
# Import from SciPy
from scipy.stats import chi2
# Import from OS
import os
from os import name
#Import Counter
from collections import Counter
# Import from platform
import platform
# Import Text colour
try:
    import colorama
    colorama.init()
except ImportError:
    pass

import warnings
warnings.filterwarnings("ignore")

# Load series of roulette numbers
series = pd.read_csv("roulette_series.csv")

#Load bet descriptions
bets = pd.read_csv("bets.csv")

# Load series of roulette numbers
enchilada = pd.read_csv("enchilada.csv")

# Removes columns with ! as first character (keep but don't use)
series = series[series.columns.drop(list(series.filter(regex='!')))]

# CONSTANTS
SCREEN_WIDTH            = 108
NUMBERS_TO_DISPLAY      = 23
RESULTS_TO_DISPLAY      = 29
VERSION                 = "EU" # US or EU

MAX_TO_SHOW             = 18

BET_INSTRUCTIONS        = True
SIGNIFICANCE_LEVEL      = 0.05

PLAY_WHOLE_ENCHILADA    = True
WHOLE_ENCHILADA_RANGE   = 5
ENCHILADA_1_TO_1        = True
ENCHILADA_1_COL_AND_DOZ = False
ENCHILADA_2_COL_AND_DOZ = True

SHOW_HOT_AND_COLD       = True
HOT_AND_COLD_RANGE      = 10

SHOW_REPEATERS          = True

SHOW_NEXT_VALUE         = True

# COLOURS
COLOUR_RED              = colorama.Fore.WHITE + colorama.Style.BRIGHT    + colorama.Back.RED
COLOUR_LIGHT_RED        = colorama.Fore.WHITE + colorama.Style.BRIGHT    + colorama.Back.LIGHTRED_EX
COLOUR_GREEN            = colorama.Fore.WHITE + colorama.Style.BRIGHT    + colorama.Back.GREEN
COLOUR_LIGHT_GREEN      = colorama.Fore.BLACK + colorama.Style.BRIGHT    + colorama.Back.LIGHTGREEN_EX
COLOUR_YELLOW           = colorama.Fore.WHITE + colorama.Style.BRIGHT    + colorama.Back.YELLOW
COLOUR_CYAN             = colorama.Fore.WHITE + colorama.Style.BRIGHT    + colorama.Back.CYAN
COLOUR_BLACK            = colorama.Fore.WHITE + colorama.Style.BRIGHT    + colorama.Back.BLACK
COLOUR_NONE             = colorama.Fore.RESET + colorama.Style.RESET_ALL + colorama.Back.RESET

#SYMBOLS - need to code difference between WIN & POSIX
ARROW_UP                = "↑"
ARROW_DOWN              = "↓"
ARROW_SAME              = "-"

if (name == "nt"):
    BORDER_LEFT             = "|"
    BORDER_RIGHT            = "|"
else:  
    BORDER_LEFT             = "⎸"
    BORDER_RIGHT            = "⎹"

OUTCOME_WIN             = COLOUR_LIGHT_GREEN + BORDER_LEFT + "W" + BORDER_RIGHT
OUTCOME_LOSS            = COLOUR_LIGHT_RED   + BORDER_LEFT + "L" + BORDER_RIGHT

LINE_CHAR_L             = "—"
LINE_CHAR_M             = "-"
LINE_CHAR_S             = "."
LINE_CHAR_O             = "~"

WHEEL_EU                = [ 0, 32, 15, 19,  4, 21,  2, 25, 17, 34,  6, 27, 13, 36, 11, 30,  8, 23, 10, 
                             5, 24, 16, 33, 1, 20, 14, 31,  9, 22, 18, 29,  7, 28, 12, 35,  3, 26]
WHEEL_NA                = [ 0, 28,  9, 26, 30, 11,  7, 20, 32, 17,  5, 22, 34, 15,  3, 24, 36, 13,  1,
                           37, 27, 10, 25, 29, 12,  8, 19, 31, 18,  6, 21, 33, 16,  4, 23, 35, 14,  2]
if (VERSION == "US"):
    WHEEL   = WHEEL_NA
else:
    WHEEL   = WHEEL_EU
    VERSION = "EU"

NUMBERS_ON_WHEEL = len(WHEEL)

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
    print(f"                            {i_threshold_3} for 2 dozens or columns.\n") 
    print(f"Number of bets:             {len(series.columns)} \n")
    print(f"Platform:                   {platform.system()}\n")

#———————————————————————————————————————————————————————————————————————————————
def print_horizontal_line(s_symbol):
    match s_symbol:
        case "L":
            s_line_char = LINE_CHAR_L
        case "M":
            s_line_char = LINE_CHAR_M
        case "S":
            s_line_char = LINE_CHAR_S
        case _:
            s_line_char = LINE_CHAR_O

    print(s_line_char * SCREEN_WIDTH)
#———————————————————————————————————————————————————————————————————————————————
def test_randomness(data):
    observed_frequencies, _ = np.histogram(data, bins=10)  # Adjust number of bins as needed
    expected_frequency = len(data) / 10  # Expected frequency for each bin assuming uniform distribution
    chi_squared_statistic = np.sum((observed_frequencies - expected_frequency)**2 / expected_frequency)
    degrees_of_freedom = len(observed_frequencies) - 1
    critical_value = chi2.ppf(1 - SIGNIFICANCE_LEVEL, degrees_of_freedom)  # Significance level 0.05
    p_value = 1 - chi2.cdf(chi_squared_statistic, degrees_of_freedom)
    
    if chi_squared_statistic > critical_value:
        s_message =  "Data is not likely random. ("
    else:
        s_message =  "Data is likely random. ("
    
    s_message = s_message + "{:.2f}".format(p_value) + ")"

    return s_message
#———————————————————————————————————————————————————————————————————————————————
# Print last numbers up to x most recent numbers spun on the roulette wheel
def recent_numbers(l_winners, i_num_played):
    clear()
    print_horizontal_line("L")
    if (len(l_winners) < NUMBERS_TO_DISPLAY):
        i_num_display = len(l_winners)
    else:
        i_num_display = NUMBERS_TO_DISPLAY
    print(f"Spins: {len(l_winners)}")

    if (i_num_played == 1):
        print(f"Last number: ", end = "")
    else:
        print(f"Last {i_num_display} numbers:", end = "")
    print(BORDER_RIGHT, end = "")
    for i_temp_loop in range(0,i_num_display):
        
        if(l_winners[(i_temp_loop)] in series['Red'].values):
            print(COLOUR_RED, end = "")
        elif(l_winners[(i_temp_loop)] in series['Black'].values):
            print(COLOUR_BLACK, end = "")
        else:
            print(COLOUR_GREEN, end = "")
        print(BORDER_LEFT, end = "")
        if (l_winners[(i_temp_loop)] == 37):
            i_winner = "00"
        else:
            i_winner = l_winners[(i_temp_loop)] 
        print( '{0: >2}'.format(i_winner), end = "")
        print(BORDER_RIGHT, end = "")

    print(COLOUR_NONE + BORDER_LEFT)
    
    if(i_num_played >= 50):
        print_horizontal_line("M")
        result = test_randomness(l_winners)
        print(result)
    print_horizontal_line("L")
    return len(l_winners)
#———————————————————————————————————————————————————————————————————————————————
def insert_stats(df, row):
    insert_loc = df.index.max()

    if pd.isna(insert_loc):
        df.loc[0] = row
    else:
        df.loc[insert_loc + 1] = row
#———————————————————————————————————————————————————————————————————————————————
# Reads input from keyboard. If value entered is an integer, between 0 and 36
# or 99, otherwise request input again.

def get_spin():
    b_valid = False
    while (not b_valid):
        s_current_number = str(input("Enter the last spin (99 to quit): "))
        if (s_current_number == "00" and VERSION == "US"):
            s_current_number = "37"
        if(s_current_number.isdigit()):
            i_current_number = int(s_current_number)
            if((0 <= i_current_number <= 37) or i_current_number == 99):
                b_valid = True
            else:
                print("Error! The value entered must be an integer between 0 and 36.\n")
        else:
            print("Error! The value entered must be an integer between 0 and 36.\n")
    return i_current_number
#———————————————————————————————————————————————————————————————————————————————
def enchilada_suggestions(l_winners): #Name taken from a style of betting from Roulette Master Youtube Video, 2024-04-06
#This whole function is poorly written. A rewrite is in order

    i_red_count            = 0
    i_black_count          = 0
    i_odd_count            = 0
    i_even_count           = 0
    i_high_count           = 0
    i_low_count            = 0
    i_c1_count             = 0
    i_c2_count             = 0
    i_c3_count             = 0
    i_d1_count             = 0
    i_d2_count             = 0
    i_d3_count             = 0
    s_bet_list             = ""
    b_multiple_suggestions = False

    for i_temp_loop in range(0,WHOLE_ENCHILADA_RANGE):
        #There must be a more efficient way to code this
        #colour
        if(l_winners[i_temp_loop] in enchilada['red'].values):
            i_red_count += 1
        if(l_winners[i_temp_loop] in enchilada['black'].values):
            i_black_count += 1  
        #odd-even         
        if(l_winners[i_temp_loop] in enchilada['even'].values):
            i_even_count += 1
        if(l_winners[i_temp_loop] in enchilada['odd'].values):
            i_odd_count += 1
        #high-low
        if(l_winners[i_temp_loop] in enchilada['low'].values):
            i_low_count += 1
        if(l_winners[i_temp_loop] in enchilada['high'].values):
            i_high_count += 1   
        #dozens
        if(l_winners[i_temp_loop] in enchilada['d1'].values):
            i_d1_count += 1   
        if(l_winners[i_temp_loop] in enchilada['d2'].values):
            i_d2_count += 1
        if(l_winners[i_temp_loop] in enchilada['d3'].values):
            i_d3_count += 1 
        #columns
        if(l_winners[i_temp_loop] in enchilada['c1'].values):
            i_c1_count += 1   
        if(l_winners[i_temp_loop] in enchilada['c2'].values):
            i_c2_count += 1
        if(l_winners[i_temp_loop] in enchilada['c3'].values):
            i_c3_count += 1 
    if(ENCHILADA_1_TO_1):
    #There must be a more efficient way to code this
    #1 to 1
        if (i_low_count < i_high_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list + " 1-18"
                b_multiple_suggestions = True
            else:
                    s_bet_list = s_bet_list +", 1-18"

        if (i_even_count < i_odd_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list + " Even"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list + ", Even"

        if (i_red_count < i_black_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list + " Red"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list + ", Red"

        if (i_black_count < i_red_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list + " Black"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list + ", Black"

        if (i_odd_count < i_even_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" Odd"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", Odd"

        if (i_high_count < i_low_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" 19-36"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", 19-36"

    if(ENCHILADA_1_COL_AND_DOZ):
    #2 to 1 - dozens
        if (i_d1_count < i_d2_count and i_d1_count < i_d3_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" First Dozen"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", First Dozen"

        if (i_d2_count < i_d1_count and i_d2_count < i_d3_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" Second Dozen"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", Second Dozen"

        if (i_d3_count < i_d1_count and i_d3_count < i_d2_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" Third Dozen"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", Third Dozen"

    #2 to 1 - columns
        if (i_c1_count < i_c2_count and i_c1_count < i_c3_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" First Column"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", First Column"

        if (i_c2_count < i_c1_count and i_c2_count < i_c3_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" Second Column"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", Second Column"

        if (i_c3_count < i_c1_count and i_c3_count < i_c2_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" Third Column"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", Third Column"


    if(ENCHILADA_2_COL_AND_DOZ):
    #2 to 1 -  2 dozens
        if (i_d1_count > i_d2_count and i_d1_count > i_d3_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" Second and Third Dozen"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", Second and Third Dozen"

        if (i_d2_count > i_d1_count and i_d2_count > i_d3_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" First and Third Dozen"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", First and Third Dozen"

        if (i_d3_count > i_d1_count and i_d3_count > i_d2_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" First and Second Dozen"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", First and Second Dozen"

    #2 to 1 - 2 columns
        if (i_c1_count > i_c2_count and i_c1_count > i_c3_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" Second and Third Column"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", Second and Third Column"

        if (i_c2_count > i_c1_count and i_c2_count > i_c3_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" First and Third Column"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", First and Third Column"

        if (i_c3_count > i_c1_count and i_c3_count > i_c2_count):
            if (b_multiple_suggestions == False):
                s_bet_list = s_bet_list +" First and Second Column"
                b_multiple_suggestions = True
            else:
                s_bet_list = s_bet_list +", First and Second Column"

    if (b_multiple_suggestions == False):
        s_bet_list = " None."
    else:
        s_bet_list = s_bet_list + "."

    print(f"Suggested Whole Enchilada bets:{s_bet_list}")
    print_horizontal_line("L")
#———————————————————————————————————————————————————————————————————————————————
def show_repeaters(numbers):
    print("Repeats:" + BORDER_RIGHT, end = "")
    sequences = []
    current_number = None
    consecutive_repeats = 0
    for number in numbers:
        if number == current_number:
            consecutive_repeats += 1
        else:
            if current_number is not None:
                sequences.append((current_number, consecutive_repeats))
            current_number = number
            consecutive_repeats = 1
    # Add the last sequence to the list
    if current_number is not None:
        sequences.append((current_number, consecutive_repeats))
    
    # Count the occurrences of each sequence
    sequence_counts = {}
    for sequence in sequences:
        sequence_counts[sequence] = sequence_counts.get(sequence, 0) + 1
    
    # Print the results
    for sequence, count in sequence_counts.items():
        number, consecutive_repeats = sequence
        if (consecutive_repeats > 1):
            if(number in series['Red'].values):
                print(COLOUR_RED, end = "")
            elif(number in series['Black'].values):
                print(COLOUR_BLACK, end = "")
            else:
                print(COLOUR_GREEN, end = "")
            if (number == 37):
                number = "00"
            print(f"{BORDER_LEFT}{number} ({consecutive_repeats}/{count}){BORDER_RIGHT}", end = "")
    print(COLOUR_NONE + BORDER_LEFT)
    print_horizontal_line("L")
#———————————————————————————————————————————————————————————————————————————————
def show_hot_and_cold(numbers, i_spins):
    # Initialize list with all possible integers
    all_numbers = list(range(0, 37))
    # Append all_numbers to l_winning_numbers
    test_numbers = numbers + all_numbers
    # Count occurrences of each integer
    counter = Counter(test_numbers)

    # Define the number of most and least common integers to select
    i_hot_cold_numbers = 3

    # Find most and least frequently occurring integers
    l_hot_numbers = counter.most_common(i_hot_cold_numbers)
    l_cold_numbers = counter.most_common()[:-i_hot_cold_numbers-1:-1]

    # Print results
    print(f"Hot {i_hot_cold_numbers}: {BORDER_RIGHT}", end = "")
    for num, count in l_hot_numbers:
        
        if(num in series['Red'].values):
            print(COLOUR_RED, end = "")
        elif(num in series['Black'].values):
            print(COLOUR_BLACK, end = "")
        else:
            print(COLOUR_GREEN, end = "")
        if (num == 37):
            num = "00"
        print(f"{BORDER_LEFT}{num}({count - 1}/{round((count-1)/i_spins*100,1)}%){BORDER_RIGHT}", end = "")
    print(COLOUR_NONE + BORDER_LEFT + "   ", end = "")

    print(f"Cold {i_hot_cold_numbers}: {BORDER_RIGHT}", end = "")
    for num, count in l_cold_numbers:

        if(num in series['Red'].values):
            print(COLOUR_RED, end = "")
        elif(num in series['Black'].values):
            print(COLOUR_BLACK, end = "")
        else:
            print(COLOUR_GREEN, end = "")
        if (num == 37):
            num = "00"
        print(f"{BORDER_LEFT}{num}({count - 1}/{round((count-1)/i_spins*100,1)}%){BORDER_RIGHT}", end = "")
    print(COLOUR_NONE + BORDER_LEFT)

    print_horizontal_line("L")  
#———————————————————————————————————————————————————————————————————————————————
def print_spin_distance(current_spin, previous_spin):
    total_spaces = len(WHEEL)
    current_index = WHEEL.index(current_spin)
    previous_index = WHEEL.index(previous_spin)
    clockwise_distance = (current_index - previous_index) % total_spaces
    anticlockwise_distance = (previous_index - current_index) % total_spaces
    print(f"{clockwise_distance}CW, {anticlockwise_distance}CCW", end = "")

#———————————————————————————————————————————————————————————————————————————————
def show_next_value(int_list):
    first_element = int_list[0]  # Get the first element in the list
    preceding_counts = {}

    for i in range(1, len(int_list)):  # Start from index 1 to avoid checking the first element against itself
        if int_list[i] == first_element:
            preceding_integer = int_list[i - 1]
            if preceding_integer not in preceding_counts:
                preceding_counts[preceding_integer] = 1
            else:
                preceding_counts[preceding_integer] += 1
    spacer = " "

    if(first_element in series['Red'].values):
        s_colour = COLOUR_RED
    elif(first_element in series['Black'].values):
        s_colour = COLOUR_BLACK
    else:
        s_colour = COLOUR_GREEN

    if (first_element == 37):
        s_first_element = "00"
        spacer          = " "
    else:
        s_first_element = str(first_element)
    s_first_element = s_colour + spacer + s_first_element + " " + COLOUR_NONE

    if preceding_counts:

        print(f"Number(s) that followed {s_first_element} previously:{BORDER_RIGHT}", end="")
        for preceding_integer, frequency in preceding_counts.items():
            if(preceding_integer in series['Red'].values):
                s_colour = COLOUR_RED
            elif(preceding_integer in series['Black'].values):
                s_colour = COLOUR_BLACK
            else:
                s_colour = COLOUR_GREEN


            print(f"{s_colour}{BORDER_LEFT}{preceding_integer}-", end="")
            print_spin_distance(first_element,preceding_integer)
            print(f"{BORDER_RIGHT}{COLOUR_NONE}", end ="")
        print(f"{BORDER_LEFT}")  # Print a newline after the output
    else:
        print(f"This is the first time that {s_first_element} has appeared. There are no previously following numbers.")

    print_horizontal_line("L")  

#———————————————————————————————————————————————————————————————————————————————
def print_results_table(l_series_names,i_threshold_1_to_1, i_threshold_2_to_1, i_threshold_2_doz_or_col, d_outcomes, d_wins, d_consecutive_wins, d_max_consecutive_wins, l_losses, i_spins, i_num_played):
    i_temp_loop = 0
    df_stats_table = pd.DataFrame(columns=['Bet', 'Threshold', 'Spins Since Win', 'Max Consecutive Losses', 'Hits Over TH', 'Max Consecutive Wins', 'Hit Percent', 'Hit Percent', 'Median', 'Mean', 'Std'])
    print('{0: ^23}'.format(''), end = "")
    print('{0: ^11}'.format('Spins Since'), end = "")
    print('{0: ^11}'.format('Max Cons.'), end = "")
    print('{0: ^11}'.format('Hits'), end = "")
    print('{0: ^11}'.format('Max'), end = "")
    print('{0: ^15}'.format('Hit %'))

    print('{0: <12}'.format('Bet'), end = "")
    print('{0: ^11}'.format('Threshold'), end = "")
    print('{0: ^11}'.format('Last Hit'), end = "")
    print('{0: ^11}'.format('Losses'), end = "")
    print('{0: ^11}'.format('>=Thld'), end = "")
    print('{0: ^11}'.format('Cons. Wins'), end = "")
    print('{0: ^15}'.format('(Expected %)'), end = "")
    print('{0: ^9}'.format('Median'), end = "") 
    print('{0: ^9}'.format('Mean'), end = "")    
    print('{0: ^9}'.format('Std Dev'))
    print_horizontal_line("M")
    for series_name in l_series_names:

        #Calculate mean number and standard deviation for spins to win
        my_list  = d_wins[series_name]
        my_array = np.array(my_list)
        my_array = my_array +1
        f_median = float("{:.1f}".format(np.median(my_array, axis=0)))
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

            #choose dynamic threshold of mean + 1 std for all triggers that dont start with -

            if (len(d_wins[series_name]) > 5 and series_name[0] != "-"):
                i_threshold = f_mean + f_std
                
            # calculate threshold (mean + 1 std)
            i_threshold = float("{:.1f}".format(i_threshold))
            if (series_name[0] != "-"):          
                s_threshold = str(i_threshold)
            else:
                s_threshold = "N/A"

            #calculate wins greater than the threshold

            temp_list = d_wins[series_name]
            temp_list = [ele for ele in temp_list if float(ele) >= i_threshold]
            if (series_name[0] != "-"):          
                s_win_over_threshold = str(len(temp_list))
            else:
                s_win_over_threshold = "N/A"

            # calculate win percentage
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

            s_win_percent = str(i_win_percent)+ s_arrow

            # calculate expected win percentage

            i_expected_percent = float("{:.1f}".format(series[series_name].count()/NUMBERS_ON_WHEEL*100))
            s_expected_percent = "(" + str(i_expected_percent)+")"


            # Add to report
            insert_stats(df_stats_table,[series_name, s_threshold, l_losses[series_name], max(d_wins[series_name]),s_win_over_threshold,  d_max_consecutive_wins[series_name], s_win_percent, i_expected_percent, f_median, f_mean, f_std  ])
            
            if ((len(series.columns) <= MAX_TO_SHOW) or (l_losses[series_name] > f_mean)):
            #set colours, yellow > mean; cyan > mean + 1 std; green > mean + 2 std; red > mean + 4 std

                if (l_losses[series_name] >= f_mean and series_name[0] != "-" ):
                    print(COLOUR_YELLOW, end = "")

                if (l_losses[series_name] >= i_threshold and series_name[0] != "-" ):
                    print(COLOUR_CYAN, end = "")

                if (l_losses[series_name] >= (i_threshold + f_std)  and series_name[0] != "-" ):
                    print(COLOUR_GREEN, end = "")

                if (l_losses[series_name] >= (i_threshold + (f_std * 3))  and series_name[0] != "-" ):
                    print(COLOUR_RED, end = "")

                # print trigger name
                print('{0: <15}'.format(series_name), end = "")

                # print threshold
                print('{0: >5}'.format(s_threshold), end = "")

                # print spins since last win
                print('{0: >10}'.format(l_losses[series_name]), end = "")

                # print most spins between wins
                print('{0: >10}'.format(max(d_wins[series_name])), end = "")

                # print wins greater than the threshold
                print('{0: >12}'.format(s_win_over_threshold), end = "")
                
                # print max consecutive wins
                print('{0: >10}'.format(d_max_consecutive_wins[series_name]), end = "")  

                # print win percentage
                print('{0: >18}'.format(s_win_percent +s_expected_percent), end = "")  

                #print median
                print('{0: >9}'.format(f_median), end = "")

                #print mean
                print('{0: >9}'.format(f_mean), end = "")

                # print standard deviation
                print('{0: >9}'.format(f_std), end = "")

                #reset colouring
                print (COLOUR_NONE, end = "")
                print("  ")

                if (series_name[0] != "-"):
                    if (len(d_outcomes[series_name]) > RESULTS_TO_DISPLAY):
                        i_numbers_to_display = RESULTS_TO_DISPLAY
                    else:
                        i_numbers_to_display = len(d_outcomes[series_name])

                    if (RESULTS_TO_DISPLAY == 1):
                        s_plural = ""
                        s_previous = ""
                    else:
                        s_plural = "s"
                        s_previous = " " + str(i_numbers_to_display)

                    if (BET_INSTRUCTIONS):
                        print(f"Previous{s_previous} outcome{s_plural}:" + BORDER_RIGHT, end = "") 
                        for s_outcome in range(0, i_numbers_to_display):
                            print(d_outcomes[series_name][s_outcome], end = "")
                        print (COLOUR_NONE + BORDER_LEFT)        

                    if (len(series) > MAX_TO_SHOW and BET_INSTRUCTIONS):
                        filtered_bets = bets[bets["Bet"].str.contains(series_name)]
                        if(len(filtered_bets) > 0):
                            print (filtered_bets["Layout"].iloc[0])
                            print ("")
                
                if (i_temp_loop % 3 == 2):
                    print_horizontal_line("S")
                i_temp_loop += 1
            #Print stats to file
            df_stats_table.to_csv('out.csv')  

#———————————————————————————————————————————————————————————————————————————————
def main():
#————————————————————————————————————————
    # Set default 
    threshold_1_to_1        =  4 
    threshold_2_to_1        =  9
    threshold_2_doz_or_col  =  3 # basically all high coverage

    #try to put this in function
    current_number           =  0
    numbers_drawn            =  0
#————————————————————————————————————————
    # Create lists to save winning numbers 
    # and variables to count losses
    series_names = series.columns.tolist()
    wins                          = {}
    outcomes                      = {}
    losses                        = {}
    consecutive_wins              = {}
    max_consecutive_wins          = {}

    for series_name in series_names:
        key = str(series_name)
        losses[key]               = 0
        wins[key]                 = []
        outcomes[key]             = []
        consecutive_wins[key]     = 0
        max_consecutive_wins[key] = 0
    winning_numbers               = []
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
                    outcomes[series_name].insert(0,OUTCOME_WIN)
                    losses[series_name]             =  0
                    consecutive_wins[series_name]   += 1
                    if (consecutive_wins[series_name] > max_consecutive_wins[series_name]):
                        max_consecutive_wins[series_name] = consecutive_wins[series_name]
                else: 
                    losses[series_name]              += 1
                    consecutive_wins[series_name]     = 0
                    outcomes[series_name].insert(0,OUTCOME_LOSS)
            numbers_drawn += 1
            winning_numbers.insert(0,current_number)
        
            #display last (x) winning_numbers
            spins = recent_numbers(winning_numbers, numbers_drawn)

            if (SHOW_HOT_AND_COLD and spins >= HOT_AND_COLD_RANGE):
                show_hot_and_cold(winning_numbers, spins)

            if (SHOW_REPEATERS):
                show_repeaters(winning_numbers)

            if (SHOW_NEXT_VALUE):
                show_next_value(winning_numbers)

            if (PLAY_WHOLE_ENCHILADA and spins >= WHOLE_ENCHILADA_RANGE):
                enchilada_suggestions(winning_numbers)
            #Print statistics
            print_results_table(series_names, threshold_1_to_1, threshold_2_to_1, threshold_2_doz_or_col, outcomes, wins, consecutive_wins, max_consecutive_wins, losses, spins, numbers_drawn)
            
            #loop back again
if __name__ == "__main__":
    main()
