global is_emulator, HX711, RFID, createEmulator

is_emulator = False

def import_as(emulator=False):
    global is_emulator, HX711, RFID, createEmulator
    is_emulator = emulator
    if not emulator:
        pass
    else:
        print("emulator")
        from pfand_emulator import HX711, RFID, createEmulator