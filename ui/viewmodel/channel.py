class Channel:
    pass

class Firework:
    "This class represents a firework"
    def __init__(self, id, controller, port):
        self.id=id
        self.controller=controller
        self.name="FW %s"%id
        self.port=port
        self.frame = None
        self.armed = False
        self.out_of_order = False
        self.timecode = 0
        self.sequence=None

    def update_entries(self, e=None):
        "Updates internal variables with ui entries fields"
        self.name=self.name_entry.get()
        timecode=self.timecode_entry.get()
        if timecode.replace(".", "").isdigit():
            self.timecode=float(timecode)
            print(self.timecode)
        else:
            showerror("Error - K-Boom", "Timecode value is not a number")
        self.sequence=self._get_sequence(self.dropdown.get())

    def _reconfigure_color(self, color):
        "Configures the color of this firework in the UI"
        self.frame.configure(background=color)
        self.name_entry.configure(background=color)
        self.timecode_entry.configure(background=color)
        self.port_label.configure(background=color)
        self.frame.update()

    def pack(self, frame):
        self.frame=Frame(frame)
        self.frame.pack()

        Label(self.frame, text=str(self.id)).pack(side=LEFT)

        self.name_entry=Entry(self.frame, validate="focusout", validatecommand=self.update_entries)
        self.name_entry.insert(0, self.name)
        self.name_entry.pack(side=LEFT)

        self.port_label=Label(self.frame, text="Port "+str(self.port)+"@Controller "+str(self.controller.id))
        self.port_label.pack(side=LEFT)

        self.timecode_entry = Entry(self.frame, validate="focusout", validatecommand=self.update_entries)
        self.timecode_entry.insert(0, "0.00")
        self.timecode_entry.pack(side=LEFT)

        self.dropdown=ttk.Combobox(self.frame, values=self._get_sequences())
        self.dropdown.set(DEFAULT_SQ_NAME)
        self.dropdown.pack(side=LEFT)
        self.dropdown.bind('<<ComboboxSelected>>', self.update_entries)

    def _get_sequences(self):
        return [sq.name for sq in sequences]

    def _get_sequence(self, name):
        for sq in sequences:
            if sq.name==name:
                return sq

    def update_dropdown(self):
        self.dropdown.configure(values=self._get_sequences())
        if self.sequence:
            self.dropdown.set(self.sequence.name)
        else:
            self.dropdown.set(sequences[0].name)

    def to_json(self):
        "Returns a json of this firework data"
        return {"name" : self.name, "port" : self.port, "id" : self.id, "controller" : self.controller.to_json(), "timecode" : self.timecode, "sequence" : self.sequence.id}
