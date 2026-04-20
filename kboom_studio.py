"""K-Boom Studio is an open-source utility software to manage your fireworks and your fireworks controllers and sequence them using timecodes."""

"""And, yeah, I know this program is absolutely horrible and messy, but don't worry, I'll refactor in a million years"""

import time
from tkinter import *
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.messagebox import *
from tkinter import ttk
import json
from kboom_config import *
from functools import partial
import threading

player=None

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


def _generate_armer(fw):
    return lambda: fw.controller.arm(fw.id)

def _generate_disarmer(fw):
    return lambda: fw.controller.disarm(fw.id)

def _generate_launcher(fw):
    return lambda: fw.launch(auto=True)

def update_entries():
    for fw in fireworks:
        fw.update_entries()

    for controller in controllers:
        controller.update_entries()

def update_dropdowns():
    for fw in fireworks:
        fw.update_dropdown()

def render_sequence():
    update_entries()
    sequence=Render()
    for fw in fireworks:
        timecode=fw.timecode
        print(timecode)
        if not timecode:
            continue
        sequence.add_step(timecode - delay - arm_delay, fw.sequence, _generate_armer(fw), 1, {"cmd" : "arm", "controller" : fw.controller.to_json()}) #Arm the controller
        sequence.add_step(timecode - delay, fw.sequence, _generate_launcher(fw), 4, {"cmd" : "launch", "firework" : fw.to_json()}) #Launch the firework
        sequence.add_step(timecode + on_time, fw.sequence, _generate_disarmer(fw), 8, {"cmd" : "disarm", "controller" : fw.controller.to_json()}) #Disarm the controller
        sequence.add_step(timecode + on_time, fw.sequence, lambda :0, 5,{"cmd": "clear", "firework": fw.to_json()})  # Disarm the controller

    sequence._recalculate_armers()
    return sequence

CURRENT_FW=1
CURRENT_CTRL=1


##########################      Core Classes        ##########################

class Controller:
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

    def arm(self, armer="auto"):
        "Arm this controller and all its fireworks"
        self.armers.append(armer)
        if not self.armed:
            if OUTPUT_ENABLED:
                backend.arm(self)
            self.armed = True
            for fw in self.fireworks:
                fw.arm()
            return True
        return False

    def disarm(self, armer="auto"):
        "DisArm this controller and all its fireworks"
        if armer in self.armers:
            del self.armers[self.armers.index(armer)]
        if not self.armers: #If there are no more armers
            self.armed=False
            if OUTPUT_ENABLED:
                backend.disarm(self)
            for fw in self.fireworks:
                fw.disarm()
            return True
        return False

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
        self.disarm_btn = Button(self.frame, text="DISARM", background="green", command=self.disarm)
        self.disarm_btn.pack(side=LEFT)
        self.arm_btn=Button(self.frame, text="ARM", background="red", command=self.arm)
        self.arm_btn.pack(side=LEFT)

    def get_name(self):
        "A kind of repr()"
        return "%s@%s"%(self.port, self.ip)

    def to_json(self):
        "Returns a json of this controller data"
        return {"ip" : self.ip, "port" : self.port, "id" : self.id, "protocol" : self.protocol}

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

    def arm(self):
        "Arm this firework"
        if self.out_of_order:
            return
        self.armed=True
        self._reconfigure_color(ARMED_COLOR)

    def disarm(self):
        "DisArm this firework"
        if self.out_of_order:
            return
        self.armed=False
        self._reconfigure_color("lightgrey")


    def ignite(self):
        "Ignites this firework"
        self._reconfigure_color(IGNITE_COLOR)

    def clear(self):
        "Clear this firework (deactivates the relay and make it out of order)"
        self._reconfigure_color(OUT_OF_ORDER_COLOR)
        #self.test_btn.configure(state=DISABLED)
        self.frame.update()
        #self.out_of_order=True
        if OUTPUT_ENABLED:
            backend.clear(self)


    def launch(self, auto=False):
        "Launches this firework"
        if not self.armed and not auto:
            return showerror("Error - K-Boom", "Please arm the controller first")
        if self.out_of_order and not auto:
            return showerror("Error - K-Boom", "This firework is out of order")
        if auto or askokcancel("Confirm - K-Boom", "Are you sure you want to K-Boom %s?" % (self.name)):
            if OUTPUT_ENABLED:
                backend.launch(self)
            tk.after(int(delay * 1000), lambda: self.ignite())
            tk.after(int(delay*1000+on_time*1000), lambda: self.clear())
            self._reconfigure_color(LAUNCH_COLOR)
            # showinfo("K-Boomed", "FW %s was K-Boomed !"%(fw+1))
        else:
            return


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

        self.test_btn = Button(self.frame, text="K-Boom", command=self.launch)
        self.test_btn.pack(side=LEFT)

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

class Sequence:
    "This class represents a sequence in the 'Sequences' frame"
    def __init__(self, name, _id):
        self.name=name
        self.id=_id
        self.duration=10.0

    def play(self):
        global player
        stop_all()
        player=render_sequence()
        player.playing_sequence=self
        player.play_thread()

    def update_entries(self, e=None):
        "Updates internal variables with ui entries fields"
        self.name = self.name_entry.get()
        self.id=self.id_entry.get()
        """duration=self.duration_entry.get()
        if not duration.isdigit():
            showerror("Error - K-Boom", "Duration value must be a number")
        else:
            duration=float(duration)
            if duration<5:
                showerror("Error - K-Boom", "Sequence must be at least 5 seconds long")
            else:
                self.duration=duration"""
        update_dropdowns()

    def pack(self, frame):
        "Packs the controller into [frame]"
        self.frame=Frame(frame)
        self.frame.pack()
        self.name_entry=ttk.Entry(self.frame)
        self.name_entry.bind("<FocusOut>", self.update_entries)
        self.name_entry.insert(0, str(self.name))
        self.name_entry.pack(side=LEFT)
        self.id_entry = ttk.Entry(self.frame)
        self.id_entry.bind("<FocusOut>", self.update_entries)
        self.id_entry.insert(0, str(self.id))
        self.id_entry.pack(side=LEFT)
        self.duration_entry=ttk.Entry(self.frame)
        self.duration_entry.bind("<FocusOut>", self.update_entries)
        self.duration_entry.insert(0, str(self.duration))
        #self.duration_entry.pack(side=LEFT)
        self.play_btn = Button(self.frame, text="Play", command=self.play)
        self.play_btn.pack(side=LEFT)

    def to_json(self):
        return {"name" : self.name, "id" : self.id, "duration" : self.duration}

class Render:
    "This class represents a rendered sequence"
    def __init__(self, sequence_data=[], playing_sequence=None):
        self.sequence_data=sequence_data
        self.playing_sequence=playing_sequence
        self.playing=True
        self.mode=MODE_STANDALONE

    def add_step(self, timecode, sequence, function, priority, command):
        #print("Adding step")
        step=(timecode, function, priority, command, sequence)
        self.sequence_data.append(step)
        self._order_sequence()

    def _order_sequence(self):
        self.sequence_data.sort(key=self._order_key)

    def _order_key(self, step):
        timecode, function, priority, command, sequence = step
        return (timecode, priority)

    def play_thread(self):
        self.playing=True
        threading.Thread(target=self.play()).start()

    def stop(self):
        self.playing=False

    def save(self):
        file_data=list()
        for timecode, func, priority, command in self.sequence_data:
            step=(timecode, command)
            file_data.append(step)
        with open(asksaveasfilename(defaultextension=".kbseq", filetypes=[("K-Boom sequence", "*.kbseq")]), "w") as f:
            json.dump(file_data, f)


    def _recalculate_armers(self):
        "Recalculates the need of the arm/disarm functions"
        new_sequence_data=[]
        for timecode, func, priority, command, sequence in self.sequence_data:
            if command["cmd"] in ["launch", "clear"]:
                new_sequence_data.append((timecode, func, priority, command, sequence))
            else:
                if func():
                    new_sequence_data.append((timecode, func, priority, command, sequence))
        self.sequence_data=new_sequence_data



    def pack(self, btn):
        print("Sequence Render data :", self.sequence_data)
        btn.configure(state=NORMAL)
        btn.configure(command=self.play_thread)
        SAV_SQ_BTN.configure(state=NORMAL)
        SAV_SQ_BTN.configure(command=self.save)

    def format_timecode(self, t):
        secs=int(t)
        min=int(secs/60)
        sec=secs%60
        cent=int((t-secs)*100)
        return "%02d:%02d:%02d"%(min, sec, cent)

    def play(self):
        t_ref=time.time() # Store the actual time reference
        lastUpdate=time.time()
        if self.playing_sequence:
            SEQUENCE_LABEL.configure(text=self.playing_sequence.name)
        else:
            SEQUENCE_LABEL.configure(text="Passive mode")
        tk.update()

        fired=[]
        while self.playing:
            t = time.time()
            actual_timecode=t-t_ref
            resync_data = resync.resync(actual_timecode, self.playing_sequence)
            if resync_data:
                resync_timecode, resync_sequence = resync_data
                #print("Resyncing to", resync_timecode)
                t_ref = t - resync_timecode
                if resync_sequence!=self.playing_sequence:
                    self.playing_sequence=find_sequence(resync_sequence)
                    if self.playing_sequence:
                        SEQUENCE_LABEL.configure(text=self.playing_sequence.name)
                    else:
                        SEQUENCE_LABEL.configure(text=resync_sequence+" (Passive mode)")

            if t - lastUpdate >= 0.1:
                TIMECODE_LABEL.configure(text=self.format_timecode(t - t_ref))
                tk.update()


            if not self.playing_sequence:
                #print("Passive mode...")
                continue

            #Check if it is fire time
            for sq_timecode, sq_func, sq_priority, sq_command, sq_sequence in self.sequence_data:
                if sq_sequence.id!=self.playing_sequence.id:
                    #print("Skipping step : not in playing sequence")
                    #print(sq_sequence.id, self.playing_sequence.id)
                    continue

                if sq_func in fired:
                    #print("Skipping step : already fired")
                    continue

                if actual_timecode>=sq_timecode:
                    if sq_priority==4:
                        print("-----------------LAUNCH----------------")
                    print("Target timecode :", sq_timecode, "Real timecode :", actual_timecode)
                    sq_func()
                    fired.append(sq_func)

            #time.sleep(0.1)


##########################      UI Functions and main       ##########################

def create_controller(frame, fw_frame):
    global controllers, CURRENT_CTRL
    controller=Controller(CURRENT_CTRL, "192.168.1.51", "1")
    controller.pack(frame, fw_frame)
    controllers.append(controller)
    CURRENT_CTRL+=1

def create_sequence():
    sequence=Sequence("Untitled", "untitled")
    sequence.pack(sequences_frame)
    sequences.append(sequence)


def generate_show_data():
    ctrl_data=[]
    for controller in controllers:
        ctrl_data.append(controller.to_json())

    fw_data = []
    for fw in fireworks:
        fw_data.append(fw.to_json())

    sq_data=[]
    for sq in sequences:
        sq_data.append(sq.to_json())

    return {"controllers" : ctrl_data, "fireworks" : fw_data, "sequences" : sq_data, "delay" : delay, "arm_delay" : arm_delay, "on_time" : on_time}

def load_show_data(data):
    global controllers, fireworks, delay, arm_delay, on_time, sequences
    for controller in controllers:
        controller.frame.destroy()
        del controller
    controllers=[]

    for fw in fireworks:
        fw.frame.destroy()
        del fw
    fireworks = []

    for sq in sequences:
        sq.frame.destroy()
        del sq
    sequences=[]

    delay=data["delay"]
    arm_delay = data["arm_delay"]
    on_time = data["on_time"]
    delay_entry.delete(0, END)
    delay_entry.insert(0, str(delay))
    arm_delay_entry.delete(0, END)
    arm_delay_entry.insert(0, str(arm_delay))
    on_time_entry.delete(0, END)
    on_time_entry.insert(0, str(on_time))

    ctrl_ids={}

    for ctrl in data["controllers"]:
        controller=Controller(ctrl["id"], ctrl["ip"], ctrl["port"])
        controller.pack(control_frame, studio_frame)
        controllers.append(controller)
        ctrl_ids[ctrl["id"]]=controller

    sq_ids={}
    for sq in data["sequences"]:
        sequence=Sequence(sq["name"], sq["id"])
        sequence.duration=sq["duration"]
        sequences.append(sequence)
        sequence.pack(sequences_frame)
        sq_ids[sequence.id]=sequence

    for fw in data["fireworks"]:
        controller=ctrl_ids[fw["controller"]["id"]]
        firework=Firework(fw["id"], controller, fw["port"])
        firework.name=fw["name"]
        firework.timecode=fw["timecode"]
        sequence=sq_ids[fw["sequence"]]
        firework.sequence=sequence
        firework.pack(studio_frame)
        firework.timecode_entry.delete(0, END)
        firework.timecode_entry.insert(0, str(firework.timecode))
        fireworks.append(firework)



    update_dropdowns()


def save_show():
    update_entries()
    update_dropdowns()
    data=generate_show_data()
    print(data)
    with open(asksaveasfilename(defaultextension=".kboom", filetypes=[("K-Boom show", "*.kboom")]), "w") as f:
        json.dump(data, f)

def open_show():
    if askokcancel("Are you sure ? - K-Boom", "Loading a new show will delete all your unsaved work. Are you sure you want to load ?"):
        with open(askopenfilename(filetypes=[("K-Boom show", "*.kboom"), ("All files", "*")])) as f:
            data=json.load(f)
        load_show_data(data)



tk=Tk()
tk.title("K-Boom Studio")

control_frame=Frame(tk)
control_frame.pack(side=LEFT)

studio_frame=Frame(tk)
studio_frame.pack(side=LEFT)

state_frame=Frame(tk)
state_frame.pack(side=LEFT)

sequences_frame=Frame(state_frame)
sequences_frame.pack()

LIVE_FRAME=Frame(state_frame)
LIVE_FRAME.pack()#side=RIGHT)

SEQUENCE_FRAME=Frame(state_frame)
SEQUENCE_FRAME.pack()#side=RIGHT)

show_FRAME=Frame(state_frame)
show_FRAME.pack()#side=RIGHT)


#Setup Controller frame
Label(control_frame, text="\nLaunch delay (in secs) :").pack()
delay_entry=Entry(control_frame)
delay_entry.insert(0, str(delay))
delay_entry.pack()
Button(control_frame, text="Change launch delay", command=change_delay).pack()

Label(control_frame, text="\nArm delay (in secs) :").pack()
arm_delay_entry=Entry(control_frame)
arm_delay_entry.insert(0, str(arm_delay))
arm_delay_entry.pack()
Button(control_frame, text="Change arm delay", command=change_arm_delay).pack()

Label(control_frame, text="\nON time (in secs) :").pack()
on_time_entry=Entry(control_frame)
on_time_entry.insert(0, str(on_time))
on_time_entry.pack()
Button(control_frame, text="Change on time", command=change_on_time).pack()

Label(control_frame, text="Controllers :").pack()
controllers=[]
fireworks=[]
sequences=[]
sequences.append(Sequence(DEFAULT_SQ_NAME, DEFAULT_SQ_ID))
Button(control_frame, text="Create Controller", command=lambda: create_controller(control_frame, studio_frame)).pack(side=BOTTOM)
create_controller(control_frame, studio_frame)

#Setup Studio frame
controllers[0].create_firework(studio_frame)
OUTPUT_ENABLED=True

#Setup sequences frame
sequences[0].pack(sequences_frame)
Button(sequences_frame, text="Play All Sequences", command=play_all).pack(side=BOTTOM)
Button(sequences_frame, text="Remote Autoplay", command=remote_autoplay).pack(side=BOTTOM)
Button(sequences_frame, text="Stop all", command=stop_all).pack(side=BOTTOM)
Button(sequences_frame, text="New Sequence", command=create_sequence).pack(side=BOTTOM)


#Setup live frame
SEQUENCE_LABEL=Label(LIVE_FRAME, text="Stopped", font=('Arial', 18))
SEQUENCE_LABEL.pack()
TIMECODE_LABEL=Label(LIVE_FRAME, text="00:00:00", font=('Arial', 21))
TIMECODE_LABEL.pack()

MSG_LABEL=Label(LIVE_FRAME, text="Waiting for MSG", font=('Arial', 15))
MSG_LABEL.pack()
backend.message_label=MSG_LABEL

SYNC_BTN = Button(LIVE_FRAME, text="Enable Auto Resync", background=DISABLED_OUT_COLOR, command=start_resync)
SYNC_BTN.pack(side=BOTTOM)

OUT_BTN = Button(LIVE_FRAME, text="Disable Output", background=ENABLED_OUT_COLOR, command=toggle_output)
OUT_BTN.pack(side=BOTTOM)


#Setup Sequence frame
SAV_SQ_BTN=Button(SEQUENCE_FRAME, text="Save Sequence", state=DISABLED)
SAV_SQ_BTN.pack(side=BOTTOM)

Button(SEQUENCE_FRAME, text="Render Sequence", command=render_sequence).pack(side=BOTTOM)

SQ_BTN=Button(SEQUENCE_FRAME, text="Play Sequence", state=DISABLED)
SQ_BTN.pack(side=BOTTOM)


#Setup show frame
SAV_BTN=Button(show_FRAME, text="Save show", command=save_show)
SAV_BTN.pack()
OPN_BTN=Button(show_FRAME, text="Open Existing show", command=open_show)
OPN_BTN.pack()


start_backend()

tk.mainloop()