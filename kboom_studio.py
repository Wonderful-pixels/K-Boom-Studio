"""K-Boom Studio is an open-source utility software to manage your fireworks and your fireworks controllers and sequence them using timecodes.
It also supports importing existing sequences to your hardware by patching ports to new ones"""

from tkinter import *
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.messagebox import *
from tkinter import ttk
import json
from kboom_config import *
from ui.patch import PatchUI
from ui.sequencer import SequencerUI
from ui.show import ShowUI
import model

player=None

class Studio:
    def __init__(self, open_project=None):
        self.tk=Tk()
        if open_project:
            self.tk.title("%s - K-Boom Studio"%open_project)
        else:
            self.tk.title("New Project - K-Boom Studio")
        self.tk.geometry("400x300+100+100")

    def run(self):
        self.tk.mainloop()


if __name__ == "__main__":
    studio=Studio()
    studio.run()