from flask import Flask, request

import threading as thrd

class ConfigVar:
    insts = {}
    def __init__(self, name, def_value):
        self.__class__.insts[name] = self
        self.__setattr__(name, def_value)
        self.name = name

class HX711:
    def __init__(self, cfg: dict):
        self.weight = ConfigVar("weight", 0)

    def getWeight(self):
        try: return float(self.weight.weight)
        except ValueError: return 0
    
class RFID:
    def __init__(self, cfg: dict):
        self.uuid = ConfigVar("uuid", "AAAAAAAA")

    def presentedCard(self):
        return self.uuid.uuid
    
def createEmulator():
    app = Flask(__name__)

    @app.route("/")
    def updateSomething():
        for i in dict(request.args).keys():
            try: ConfigVar.insts[i].__setattr__(i, dict(request.args)[i])
            except KeyError: return "Does not found value with provided key"
            return f"Emulator update successfull, {i}: {dict(request.args)[i]}"
        
    thrd.Thread(target=app.run, args=("0.0.0.0", 5050)).start()