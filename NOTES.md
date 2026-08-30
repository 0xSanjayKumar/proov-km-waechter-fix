# What I checked, and what the agent got wrong

1. Before the code was running // that round off the value which in this case the value was from 0- 1 so the decimal value was round to 0.

2. Also the silent bug that was converting the km to miles, in the variable it say miles per km, that means the value supposed to be 0.621 and not 1.609 (which km per miles)

## What the agent got wrong

script crashed at runtime with a UnicodeEncodeError. The agent had to fix it after seeing the error.

## What I checked before I accepted its work

I ran the verify.py script to validate if everything passed. 

## What the data actually said

From the data it was observed that the odometer_km and age_years Cohen's d was less than 0.01 for both breakdown cars and the healthy cars and mostly it was identical. But these 3 parameters load factor, average daily km & km since last service was used to measure the habits of a car to predict whether it will breakdown, before it actually does.