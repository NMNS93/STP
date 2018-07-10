#!/usr/env/bin python3
"""
Generate the graphical user interface for the MRI quality assurance software.
"""

import tkinter.filedialog
from tkinter import *

import mriqa

class MRI():
    """Class containing tkinter objects for the graphical user interface.
    Args:
        parent - Instance of a tkinter.Tk() object.
    """
    def __init__(self, parent):
        """Create widgets and properties for the user interface"""
        # Assign the Tkinter window object passed to this class as a variable.
        self.parent = parent
        # Create a Frame object in the GUI window for holding widgets
        self.mainContainer = Frame(parent, width=500, height=500)
        # All objects and widgets must be made visible using tkinter object.pack() or object.grid().
        self.mainContainer.pack()

        # Set a title large-font title in the window
        self.windowlabel = Label(self.mainContainer, text="MRI QA", font=("Arial Bold", 30))
        self.windowlabel.pack()        
        # Set a disclaimer below the title.
        self.windowlabel = Label(self.mainContainer, text="WARNING: Not validated for clinical use", font=("Arial Bold", 15))
        self.windowlabel.pack()
        # Set a default prompt string for the input directory. This is changed when the user clicks 
        # the 'Browse' button and is provided as input for the MRI QA script.
        self.fname = Label(self.mainContainer, text="<Select a directory>")
        self.fname.pack()

        # Create tkinter.IntVar() variables for the checkboxes in the GUI.
        self.var = IntVar()
        self.var.set(1)
        self.var2 = IntVar()
        self.var2.set(1)

        # Create the checkbutton widgets for selecting mri qa modules.
        self.check = Checkbutton(self.mainContainer, text="Image Handling: Rename", variable=self.var,
            onvalue=1, offvalue=0)
        self.check.pack()
        self.check2 = Checkbutton(self.mainContainer, text="Image Analysis: Uniformity", variable=self.var2)
        self.check2.pack()

        # Create the browse button widget for selecting input directory.
        # This widget is bound to the function selectDirectory() below
        self.browse = Button(self.mainContainer, text="Browse", command = self.selectDirectory, width=10)
        self.browse.bind("<Return>", self.selectDirectory)
        self.browse.pack()

        # Create a container for the 'Run' and 'Cancel' buttons of the GUI and add to the GUI.
        self.runcontainer = Frame(parent)
        self.runcontainer.pack()
        self.button1 = Button(self.runcontainer, text="RUN", background="green", command=self.run)
        self.button1.pack(side=LEFT)
        self.button2 = Button(self.runcontainer, text="Cancel", background="red")
        self.button2.pack(side=LEFT)
        self.button2.bind("<Button-1>", self.cancelClick)

        # Create a toggle variable to be switched only once a directory has been selected by the user.
        self.directory_selected = 0


    def cancelClick(self, event):
        """Destroy all windows and close the GUI."""
        self.parent.quit()

    def selectDirectory(self):
        """Select the input directory containing MRI QA files for analysis."""
        filename = tkinter.filedialog.askdirectory()
        self.fname["text"] = filename
        # Toggle variable indicating a directory has been selected.
        self.directory_selected = 1

    def popupbox(self, message, parent_destroy):
        """A popup to be displayed when the analysis is complete.
        Args:
            parent - Instance of a tkinter.Tk() object
            parent_destroy (int) - Value for closing the popupbox (0) or the entire GUI (1)"""
        win = Toplevel()
        win.title("MRI QA")
        msg = Message(win, text=message, width=200)
        msg.pack()
        cmd = self.parent.quit if parent_destroy else win.destroy
        button = Button(win, text="Dismiss", command=cmd)
        button.pack()

    def run(self):
        """Call MRI QA with the appopriate parameters based on GUI"""
        # If both checkbox options are selected, set module variable to 'all', else run appropriate module
        if self.var.get() and self.var2.get():
            module = 'all'
        # Else run approprite module
        elif self.var.get():
            module = 'rename'
        elif self.var2.get():
            module = 'uniformity'
        # Do nothing if no checkboxes were ticked
        else:
            module = 0

        # If a module has been ticked and a directory has been selected, call the mri qa command
        if module and self.directory_selected:
            args = [module, '-i', self.fname["text"], '-c', 'config.ini']
            print(args)
            mriqa.main(args)
            self.popupbox('Analysis complete.', 1)
        else:
            self.popupbox('Please select a directory and module', 0)


def main():
    """Setup and display graphical user interface.
    """
    # Set main GUI window object
    root = Tk()
    # Title GUI window
    root.title("MRI QA")
    # Set default size of GUI window
    root.geometry("400x200")
    # Create GUI based on tkinter setup in the MRI class
    gui = MRI(root)
    # Listen for events from the GUI user
    root.mainloop()

if __name__ == "__main__":
    main()
