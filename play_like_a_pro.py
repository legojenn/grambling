#Title:          Roulette Number Predictor for Play Like a Pro
#Started:        2024-01-22
#Last Modified:  2024-01-22
#Python version: 3.10.12
#Pandas version: 2.1.4
#Purpose:        Reads input from keyboard for last value spun in roulette
#                and number of spins since the bet won, max number of spins
#                between wins and median number of spins.
#
#Note:           The code is completely unoptimised for readability.  

#Load Pandas & NumPy
import pandas as pd
import numpy  as np
import os

#set initial values
series_red     = pd.DataFrame([1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36])
series_black   = pd.DataFrame([2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35])
series_low     = pd.DataFrame([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18])
series_high    = pd.DataFrame([19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36])
series_odd     = pd.DataFrame([1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35])
series_even    = pd.DataFrame([2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36])

wins_red        = []
wins_black      = []
wins_odd        = []
wins_even       = []
wins_low        = []
wins_high       = []

losses_red     = 0
losses_black   = 0
losses_low     = 0
losses_high    = 0
losses_odd     = 0
losses_even    = 0

current_number = 0

max_difference = 2

place_holder   = " "

# Clearing the Screen
os.system('clear')


# Main Loop

while (current_number !=99):
    
    current_number = int(input("Enter the last spin (99 to quit): "))

    print(" ")

    if (current_number in series_black.values):
        wins_black.append(losses_black + 1)
        losses_black = 0;
        losses_red += 1;
    
    if (current_number in series_red.values):
        wins_red.append(losses_red + 1)
        losses_red = 0;
        losses_black += 1;
        
    if (current_number in series_low.values):
        wins_low.append(losses_low + 1)
        losses_low = 0;
        losses_high += 1;  
    
    if (current_number in series_high.values):
        wins_high.append(losses_high + 1)
        losses_high = 0;
        losses_low += 1;
    
    if (current_number in series_odd.values):
        wins_odd.append(losses_odd + 1)
        losses_odd = 0;
        losses_even += 1;
        
    if (current_number in series_even.values):
        wins_even.append(losses_even + 1)
        losses_even = 0;
        losses_odd += 1;

    if (current_number == 0):
        losses_red   += 1;
        losses_black += 1;
        losses_odd   += 1;
        losses_even  += 1;
        losses_high  += 1;
        losses_low   += 1;

    if (len(wins_red) > 0):
        print("Spins since last red win   ", end ="")
        if (losses_red < 10):
            print (place_holder, end ="")
        print (str(losses_red), end = "")
        print(" - Max spins between wins ", end = "") 
        if (max(wins_red) < 10):
            print (place_holder, end ="")
        print (str(max(wins_red)), end = "")
        print(" - Top quintile : ", end ="")
        if (max(str(np.percentile(wins_red, 80) < 10))):
            print (place_holder, end ="")        
        print(str(float("{:.1f}".format(np.percentile(wins_red, 80)  ))), end = "")
        print (".")

    if (len(wins_black) > 0):
        print("Spins since last black win ", end ="")
        if (losses_black < 10):
            print (place_holder, end ="")
        print (str(losses_black), end = "")
        print(" - Max spins between wins ", end = "") 
        if (max(wins_black) < 10):
            print (place_holder, end ="")
        print (str(max(wins_black)), end = "")
        print(" - Top quintile : ", end ="")
        if (max(str(np.percentile(wins_black, 80) < 10))):
            print (place_holder, end ="")        
        print(str(float("{:.1f}".format(np.percentile(wins_black, 80)  ))), end = "")
        print (".")

    if (len(wins_odd) > 0):
        print("Spins since last odd win   ", end ="")
        if (losses_odd < 10):
            print (place_holder, end ="")
        print (str(losses_odd), end = "")
        print(" - Max spins between wins ", end = "") 
        if (max(wins_odd) < 10):
            print (place_holder, end ="")
        print (str(max(wins_odd)), end = "")
        print(" - Top quintile : ", end ="")
        if (max(str(np.percentile(wins_odd, 80) < 10))):
            print (place_holder, end ="")        
        print(str(float("{:.1f}".format(np.percentile(wins_odd, 80)  ))), end = "")
        print (".")

    if (len(wins_even) > 0):
        print("Spins since last even win  ", end ="")
        if (losses_even < 10):
            print (place_holder, end ="")
        print (str(losses_even), end = "")
        print(" - Max spins between wins ", end = "") 
        if (max(wins_even) < 10):
            print (place_holder, end ="")
        print (str(max(wins_even)), end = "")
        print(" - Top quintile : ", end ="")
        if (max(str(np.percentile(wins_even, 80) < 10))):
            print (place_holder, end ="")        
        print(str(float("{:.1f}".format(np.percentile(wins_even, 80)  ))), end = "")
        print (".")

    if (len(wins_low) > 0):
        print("Spins since last low win   ", end ="")
        if (losses_low < 10):
            print (place_holder, end ="")
        print (str(losses_low), end = "")
        print(" - Max spins between wins ", end = "") 
        if (max(wins_low) < 10):
            print (place_holder, end ="")
        print (str(max(wins_low)), end = "")
        print(" - Top quintile : ", end ="")
        if (max(str(np.percentile(wins_low, 80) < 10))):
            print (place_holder, end ="")        
        print(str(float("{:.1f}".format(np.percentile(wins_low, 80)  ))), end = "")
        print (".")

    if (len(wins_high) > 0):
        print("Spins since last high win  ", end ="")
        if (losses_high < 10):
            print (place_holder, end ="")
        print (str(losses_high), end = "")
        print(" - Max spins between wins ", end = "") 
        if (max(wins_high) < 10):
            print (place_holder, end ="")
        print (str(max(wins_high)), end = "")
        print(" - Top quintile : ", end ="")
        if (max(str(np.percentile(wins_high, 80) < 10))):
            print (place_holder, end ="")        
        print(str(float("{:.1f}".format(np.percentile(wins_high, 80)  ))), end = "")
        print(".")
    print(" ")
    print("Bets that are greater than its 4th quintile:", end = "")
    if (len(wins_red) > 0):
        if (losses_red > np.percentile(wins_red, 80) ):
            print(" red", end ="")
    if (len(wins_black) > 0):
        if (losses_black > np.percentile(wins_black, 80) ):
            print(" black", end ="")
    if (len(wins_even) > 0):
        if (losses_even > np.percentile(wins_even, 80) ):
            print(" even", end ="")
    if (len(wins_odd) > 0):
        if (losses_odd > np.percentile(wins_odd, 80) ):
            print(" odd", end ="")
    if (len(wins_low) > 0):
        if (losses_low > np.percentile(wins_low, 80) ):
            print(" low", end ="")
    if (len(wins_high) > 0):
        if (losses_high > np.percentile(wins_high, 80) ):
            print(" high", end ="")
    print(".")

    print("Bets that are within "+ str(max_difference) + " spins of the max:", end = "")
    if (len(wins_red) > 0):
        if ((max(wins_red) - max_difference) <= losses_red ):
            print(" red", end ="")
    if (len(wins_black) > 0):
        if ((max(wins_black) - max_difference) <= losses_black ):
            print(" black", end ="")
    if (len(wins_even) > 0):
        if ((max(wins_even) - max_difference) <= losses_even ):
            print(" even", end ="")
    if (len(wins_odd) > 0):
        if ((max(wins_odd) - max_difference) <= losses_odd ):
            print(" odd", end ="")
    if (len(wins_low) > 0):
        if ((max(wins_low) - max_difference) <= losses_low ):
            print(" low", end ="")
    if (len(wins_high) > 0):
        if ((max(wins_high) - max_difference) <= losses_high ):
            print(" high", end ="")

    print(".")

    print('\n' * 2)

print ("Done")
