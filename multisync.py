import socket
import struct
import threading

FPP_IP = "0.0.0.0"
FPP_PORT = 32320  # FPP MultiSync port
last_sync=None
started=False

def start_remote():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FPP_IP, FPP_PORT))
    thread = threading.Thread(target=run_remote, args=(sock,), daemon=True)
    thread.start()
    print("UDP server started in background.")

def run_remote(sock):
    global last_sync, started
    print(f"Listening for FPP MultiSync packets on port {FPP_PORT}...\n")

    while True:
        data, addr = sock.recvfrom(2048)
        print(data)
        if len(data) < 17:
            continue  # Too short to be valid

        header = data[0:4].decode(errors="ignore")
        if header != "FPPD":
            continue  # Not an FPP packet

        packet_type = data[4]
        extra_len = struct.unpack("<H", data[5:7])[0]
        sync_packet_type = data[7]
        file_type = data[8]
        frame_number = struct.unpack("<I", data[9:13])[0]
        elapsed_time = struct.unpack("<f", data[13:17])[0]
        filename = data[17:].split(b'\x00', 1)[0].decode(errors="ignore")
        sequence_name=(filename.replace(".fseq", "")
                       .replace(".wav", "")
                       .replace(".mp3", "")
                       .replace(".mp4", "")
                       .replace(".mov", "")
                       .replace(".mpg", "")
                       .replace(".jpg", "")
                       .replace(".png", ""))
        last_sync=elapsed_time, sequence_name
        started=True
        if file_type==0:
            pass
            """print(f"  Elapsed Time: {elapsed_time:.3f}s")
            print(f"  Filename: {filename}")
            print("-" * 50)"""

def resync(timecode, sequence):
    global last_sync
    if not last_sync:
        return False
    timecode, sequence=last_sync
    last_sync=None
    return timecode, sequence


def start():
    start_remote()
    return True

if __name__=="__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FPP_IP, FPP_PORT))
    run_remote(sock)