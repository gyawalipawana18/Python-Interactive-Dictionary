"""Interactive Dictionary using Tkinter module"""

import threading

# For text to speech
import pyttsx3
engine = pyttsx3.init('sapi5')
voices= engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Difflib librry helps to find the best match of the word out of the list
from difflib import SequenceMatcher, get_close_matches

# Sqlite module to work with database
import sqlite3 as sq 
conn = sq.connect("dictionary.pd")
cursor= conn.cursor()

"""Tkinter GUI"""
from tkinter import *
from tkinter import PhotoImage
from tkinter import messagebox

# Gui window
window = Tk()
window.title("Interactive Dictionary")
# window.geometry('1080x720')
window.resizable(0,0)
window.configure(bg="#06283D")

# constants
CLOSE_MATCH_FOUND = "closeMatchFound"
NOT_FOUND_IN_DICTIONARY = "notFoundInDictionary"
AUDIO_THREAD = None

# To search for the word in the dictionary and returning the list of result
def search(word):
    list_of_result = []
    l_word = word.lower().rstrip()
    u_word = word.capitalize().rstrip()
    cursor.execute(f"SELECT Definition FROM dictionary WHERE Expression = '{l_word}' or Expression = '{u_word}';")
    result = cursor.fetchall()
    if len(result)!=0:
        for meanings in result:
            for expression in meanings:
                list_of_result.append(expression.rstrip())
        return list_of_result
    else:
        closeMatchFound = check_close_match(word)
        if closeMatchFound:
            return CLOSE_MATCH_FOUND
        else:
            return NOT_FOUND_IN_DICTIONARY


# To get the close matches of the given word in the database table
# And returning the final result
def check_close_match(word):
    global window
    cursor.execute("SELECT Expression from dictionary;") #query to get all the expressions from dictionary
    raw_list_of_expressions = cursor.fetchall() #fetching the list of the expressionss
    list_of_expressions = []
    for tup in raw_list_of_expressions:
        for expression in tup:
            if expression!=None:
                list_of_expressions.append(expression.rstrip())
    close_match = get_close_matches(word, list_of_expressions, n=5, cutoff=0.8)#getting the close match
    if len(close_match) != 0:
        new_word = close_match[0]

        # Ask user if the word he/she wanted to search is this close_match one
        textBox.delete("1.0", END)
        textBox.insert(END, f"Do you mean '{new_word}' instead of '{word}'?")
        yesButton = Button(window, text="Yes", command=lambda: proceed("Y", new_word))
        yesButton.grid(row=3, column=1, padx=10, sticky="W")
        noButton = Button(window, text="No", command=lambda:  proceed("N", new_word))
        noButton.grid(row=4, column=1, padx=10, sticky="W")
        
        speakFromTextBox()

        return CLOSE_MATCH_FOUND
    else:
        return NOT_FOUND_IN_DICTIONARY


# To proceed after finding the new word list
def proceed(confirm, new_word):
    if confirm.lower()=="y": # If user press "Yes"
        entry.delete(0,END)
        entry.insert(END,f"{new_word}")
        result = search(new_word)
    elif confirm.lower()=="n": #If user press "No"
        result = ["There is not such word in the dictionary."]
    
    yn_destroy() # To destroy the yes/no button
    show_result(result)
    return True


# To destroy the yes/no button
def yn_destroy():        
    yn_child = window.winfo_children()
    for i in yn_child[-2:]:
        i.destroy()


# To find the meaning
def find_meaning(e=None):
    word = word_var.get()
    if not word:
        show_result(["Please type a word!"])
        return False
    result = search(word)
    if result == CLOSE_MATCH_FOUND:
        return False
    if result == NOT_FOUND_IN_DICTIONARY:
        show_result(["There is no such word in the dictionary!"])
        return False
    show_result(result)
    return True


# To show the result
def show_result(result):
    global textBox
    textBox.delete("1.0",END)
    for index, expression in enumerate(result):
        if len(expression) != 0:
            meaning_to_insert = f"{expression}\n"
            meaning_to_insert = (f"Meaning {index+1}: " + meaning_to_insert) if len(result)>1 else meaning_to_insert
            textBox.insert(END, meaning_to_insert)
    
    speakFromTextBox()

# About the dictionary
def about_dict():
    information = """
    Interactive dictionary!
    Version 2.0
    By Sachin,Pawana,Puspa
    
    Features:
    > Interactive interface
    > Get the word suggestions in case of typo.
    """
    messagebox.showinfo("Information", information)


def speakFromTextBox():
    global AUDIO_THREAD
    AUDIO_THREAD = threading.Thread(target=speak, args=(textBox.get("1.0", END),), daemon=True)
    textBox.after(10, lambda : AUDIO_THREAD.start())


def speak(text):
    engine.say(text) 
    engine.runAndWait()


# Entry
word_var = StringVar()
entry = Entry(window, textvariable=word_var, width=30, font=("TKDefault", 12))
entry.grid(row=0, column=0, sticky="E", pady=15, padx=10)
entry.bind('<Return>', find_meaning)

# Search button
search_btn = Button(window, text="Search", command=find_meaning, width=20)
search_btn.grid(row=0, column=1, sticky="W", pady=15, padx=10)

# Audio button
speak_btn = Button(window, text="Speak",
                command=lambda: speakFromTextBox(), 
                width=6)
speak_btn.grid(row=2, column=2, pady=15, padx=10, sticky="N")

def clear():
    textBox.delete("1.0", END)

# Audio button
clear_btn = Button(window, text="Clear", command=clear, width=6)
clear_btn.grid(row=3, column=2, pady=15, padx=10, sticky="N")

# About button
about_btn = Button(window, text="About", command=about_dict, width=6)
about_btn.grid(row=4, column=2, pady=15, padx=10, sticky="N")

# About button
exit_btn = Button(window, text="Exit", command=lambda : window.destroy(), width=6)
exit_btn.grid(row=5, column=2, pady=10, padx=10, sticky="N")

# Text Button
textBox = Text(window)
textBox.grid(row=2, column=0, columnspan=2, rowspan=20, pady=15, padx=10)

# For responsiveness
n_columns, n_rows = window.grid_size()
for i in range(n_rows):
    Grid.rowconfigure(window, i, weight=1)
for i in range(n_columns):
    Grid.columnconfigure(window, i, weight=1)

speak("Opening the interactive dictionary. Please wait.")

# Mainloop
window.mainloop()