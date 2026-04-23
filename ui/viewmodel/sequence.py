class Sequence:
    pass

class Cue:
    pass

'''class Sequence:
    "This class represents a sequence in the 'Sequences' frame"
    def __init__(self, name, _id):
        self.name=name
        self.id=_id
        self.duration=10.0

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

    def to_json(self):
        return {"name" : self.name, "id" : self.id, "duration" : self.duration}
'''

'''class Render:
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
'''