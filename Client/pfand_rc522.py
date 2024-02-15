from pirc522 import RFID as rfid
import threading as thrd

class RFID:
    def __init__(self, cfg: dict, logger):
        self.logger = logger
        self.device = rfid()
        thrd.Thread(target=self).start()
        self.logger("RFID main thread started")
        self.uuid = [False, ""]

    def __call__(self):
        try:
            while 1:
                (error, data) = self.device.request()
                if not error:
                    (error, uuid) = self.device.anticoll()
                    self.uuid = [True, uuid]
                    self.logger(f"new card presented: {uuid}")
        except Exception as e:
            self.logger(f"ERROR --- in RFID main thread: {e}")

    def presentedCard(self):
        val = tuple(self.uuid)
        if self.uuid[0]: self.uuid[0] = False
        return val

if __name__ == "__main__":
    from pfand_types import Logger
    from time import sleep
    rc522 = RFID({}, Logger)
    while 1:
        sleep(1.5)
        print(rc522.presentedCard())