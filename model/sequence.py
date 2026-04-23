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

class Sequence:
    pass

class Cue:
    pass
