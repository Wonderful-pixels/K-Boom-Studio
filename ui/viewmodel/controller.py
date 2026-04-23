def change_delay():
    global delay
    value=delay_entry.get()
    if not value.replace(".", "").isdigit() or value.count(".")>1:
        showerror("Error - K-Boom", "Delay is not numeric")
        return
    delay=float(value)

def change_arm_delay():
    global delay
    value=arm_delay_entry.get()
    if not value.replace(".", "").isdigit() or value.count(".")>1:
        showerror("Error - K-Boom", "Delay is not numeric")
        return
    arm_delay=float(value)

def change_on_time():
    global delay
    value=on_time_entry.get()
    if not value.replace(".", "").isdigit() or value.count(".")>1:
        showerror("Error - K-Boom", "ON time is not numeric")
        return
    on_time=float(value)

"""class Controller:
    "This class represents a controller"
    def __init__(self, _id, ip, port):
        self.ip=ip
        self.port=port
        self.id=_id
        self.fireworks = []
        self.protocol = "maestro"
        self.frame = None
        self.current_port = 1
        self.armed = False
        self.armers = []

    def create_firework(self, frame):
        global CURRENT_FW
        firework=Firework(CURRENT_FW, self, self.current_port)
        firework.pack(frame)
        self.fireworks.append(firework)
        fireworks.append(firework)
        CURRENT_FW+=1
        self.current_port+=1

    def update_entries(self):
        "Updates internal variables with ui entries values"
        self.ip=self.ip_entry.get()
        self.port=self.port_entry.get()

    def pack(self, frame, fw_frame):
        "Packs the controller into [frame]"
        self.frame=Frame(frame)
        self.frame.pack()
        Label(self.frame, text=str(self.id)).pack(side=LEFT)
        self.ip_entry=Entry(self.frame, validate="focusout", validatecommand=self.update_entries)
        self.ip_entry.insert(0, str(self.ip))
        self.ip_entry.pack(side=LEFT)
        self.port_entry = Entry(self.frame)
        self.port_entry.insert(0, str(self.port))
        self.port_entry.pack(side=LEFT)
        self.create_btn=Button(self.frame, text="Create FW", command=lambda:self.create_firework(fw_frame))
        self.create_btn.pack(side=LEFT)

    def get_name(self):
        "A kind of repr()"
        return "%s@%s"%(self.port, self.ip)

    def to_json(self):
        "Returns a json of this controller data"
        return {"ip" : self.ip, "port" : self.port, "id" : self.id, "protocol" : self.protocol}
"""

class Controller:
    pass
