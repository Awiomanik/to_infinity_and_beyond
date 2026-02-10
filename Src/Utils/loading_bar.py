# Project Description:
#
# Overview:
# This project is a Python implementation designed to provide a visual representation of progress
# during computational tasks. It enables users to incorporate an intuitive loading bar with real-time updates,
# estimated time remaining, and other relevant information.
#
# ---
#
# Class: LoadingBar
#
# Initialization:
# - Description: Initializes the LoadingBar instance.
# - Parameters:
#   - total: Number of calculations or iterations to complete (integer).
#   - additional_info: Additional information to display (string).
#
# Update Method:
# - Description: Updates the loading bar with progress information.
# - Parameters:
#   - iteration: Current iteration (indexing from 1) (integer).
#   - additional_info: Additional information about the current state (string).
#   - skip_every_other: Updates the loading bar every other iteration (default=0, updates every iteration) (integer).
# - Returns: Percentage of completion (skipping percentages if skip_every_other is set).
#
# Close Method:
# - Description: Finalizes the loading bar, displaying total time, total iterations, and additional information.
# - Parameters:
#   - display_statement: Whether to display a summary statement with the total number of calculations and time taken (boolean, default=True).
#   - additional_info: Additional information to display (string).
#   - clear_loading_bar: Whether to leave the loading bar visible in the console (boolean, default=True).
# - Returns: Total time taken to complete all calculations in seconds (float).
#
# ---
#
# Usage Example:
#
# tot = 200
# tim = 1
# bar = LoadingBar(tot) # OUTPUT: | 0% |════════════════════════════════════════════════════════════════════════════════════| 0/200 | Avgerage | Estimated |
#
# for i in range(tot):
#     time.sleep(tim)
#     bar.update(i + 1) # OUTPUT: | 3% |▰▰═════════════════════════════════════════════════════════════════════════════════| 7/200 | Avg = 1s | Est = 3min |
#
# bar.close(clear_loading_bar=False) OUTPUT: | 100% |▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰| 2/2 | Avg = 1s | Est = 0s | 
#                                            Finnished 2 calculations in 3.33min.
#
# Example 2:
#
# tot = 3
# tim = 10
# bar = LoadingBar(tot, "let's calculate stuff") # OUTPUT: | 0% |═══════════════════════════════════════════════════════════════| 0/3 | let's calculate stuff | Avgerage | Estimated |
#
# for i in range(tot):
#     time.sleep(tim)
#     bar.update(i+1, f"squere of i = {i**2}", 2) # OUTPUT: | 66% |▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰═══════════════| 2/3 | squere of i = 1 | Avg = 10s | Est = 10s |
#
# bar.close(True, additional_info="Well that was it") # OUTPUT: Finnished 3 calculations in 30.03s. (Well that was it)
#
# by Wojciech Kośnik-Kowalczuk (WKK)

import shutil
import time

class LoadingBar():
    # Atributes
    _PROGRESS_BAR_CHAR = '\u25B0'
    _EMPTY_BAR_CHAR = '\u2550'
    _total = None
    _start = None
    _percentage = None

    # Methods
    def __init__(self, total:int, additional_info:str=None) -> None:
        '''Initializes the loading bar by setting up \
        attributes and displaying an empty loading bar.
        
        Args:
        - total: Number of all calculations (iterations) to make.
        - additional_info: Additional information to display.
        '''
        # set atrributes
        self._total = total
        self._start = time.time()
        self._percentage = 0

        # prepare loading bar
        percent_string = f"| 0% |"
        info_string = f"| 0/{self._total} | " + \
                    ((additional_info + " | ") if additional_info else '') + \
                    f"Avgerage | Estimated |"
        loading_bar_size = shutil.get_terminal_size()[0] - len(info_string) - 9
        
        # display empty loading bar
        print('\r' + percent_string + self._EMPTY_BAR_CHAR * loading_bar_size + info_string, end='')

    def update(self, iteration:int, additional_info:str=None, skip_every_other:int=0) -> int:
        '''Updates the loading bar.

        Args:
        - iteration: Current iteration (indexing from 1!).
        - additional_info: Additional information about the current state.
        - skip_every_other: Update loading bar displays every \
        other iteration (default=0 - every iteration).
        
        Returns:
        - percentage (skipping percentages if skip_every_other is set).
        '''
        # skip every other iteration
        if not skip_every_other or (skip_every_other and iteration%skip_every_other == 0):

            # initialize nmerical variables
            current_time = time.time()
            self._percentage = int(iteration/self._total * 100)
            average_time = (current_time - self._start) / iteration
            estimated_time = average_time * (self._total - iteration)

            # set time unit for average_time
            if average_time > 59: # > min
                average_time_string = f"Avg = {average_time/60:.0f}min | "
            elif average_time > 1: # > s
                average_time_string = f"Avg = {average_time:.0f}s | "
            else: # average_time < 1: # < s
                average_time_string = f"Avg = {average_time*1000:.0f}ms | "

            # set time unit for estimated_time
            if estimated_time > 3599: # > hour
                estimated_time_string = f"Est = {estimated_time/3600:.0f}h | "
            elif estimated_time > 59: # > min
                estimated_time_string = f"Est = {estimated_time/60:.0f}min | "
            else: # estimated_time < 60:
                estimated_time_string = f"Est = {estimated_time:.0f}s | "
            
            # initialize strings
            percent_string = f"| {self._percentage}% |"
            info_string = f"| {iteration}/{self._total} | " + \
                        ((additional_info + " | ") if additional_info else '') + \
                        average_time_string + estimated_time_string

            # initialize size
            loading_bar_size = shutil.get_terminal_size()[0] - len(percent_string) - len(info_string) - 1

            # print all
            print("\r" + percent_string + \
                    self._PROGRESS_BAR_CHAR * (int(self._percentage / 100 * loading_bar_size)) + \
                    self._EMPTY_BAR_CHAR * (int((100 - self._percentage) / 100 * loading_bar_size)) + \
                    info_string, end='')

        return self._percentage

    def close(self, display_statement:bool=True, additional_info:str=None, clear_loading_bar:bool=True) -> float:
        '''
        Finalizes the loading bar by displaying total time, \
        total iterations and additional information.
        
        Args:
        - display_statement: Whether to display a summary statement \
        with the total number of calculations and time taken.
        - additional_info: Additional information to display.
        - clear_loading_bar: Whether to leave the loading bar visible in the console.
        
        Returns:
        - Total time taken to complete all calculations in seconds.
        '''
        # clear loading bar
        if clear_loading_bar:
            print('\r', end='')
        else:
            print()

        # get total time
        total_time = time.time() - self._start

        # display final information
        statement = ''
        if display_statement:

            # set time units if necessary
            if total_time > 3599: # > hour
                total_time_str = f"{total_time/3600:.2f}h"
            elif total_time > 59: # > min
                total_time_str = f"{total_time/60:.2f}min"
            else: # total_time < min
                total_time_str = f"{total_time:.2f}s"

            # set statement
            statement = f"\rFinnished {self._total} calculations in {total_time_str}."
        
        # append additional info
        statement += ((' (' if statement else '') + additional_info + (')' if statement else '')) \
            if additional_info else ''

        print(statement, end='')
        
        # clear rest of the line
        if clear_loading_bar:
            print(' ' * (shutil.get_terminal_size()[0] - len(statement) - 1))

        return total_time
