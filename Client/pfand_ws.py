import websockets as wbs
import asyncio
import json
import pfand_crypto as sec
import threading as thrd
from enum import Enum

class WsState(Enum):
    DOESNT_CONNECT = 21
    AUTHING = 22
    FAILED = 23
    READY = 24
    MESSAGE = 25
    FAILED_AUTHDATA = 26

class WsClient:
    def __init__(self, config: dict, logger: object):
        self.cfg = config
        self.logger = logger
        self.state = WsState.DOESNT_CONNECT
        self.msg = []
        thrd.Thread(target=self.run_wbs).start()

    def update_config(self):
        json.dump(self.cfg, open("Client/pfand_configs.json", 'w'))

    async def wbs_runner(self):
        self.logger("trying to connect...")
        async for ws in wbs.connect('ws://localhost:9090'):
            self.logger("connected to ws server")
            self.state = WsState.AUTHING
            msg = json.loads(await ws.recv())
            if msg['status'] != "ok":
                self.logger("first pre-auth message status err, reconect in 5 secs")
                self.state = WsState.FAILED
                await asyncio.sleep(5)
                self.logger("reconnect")
                self.state = WsState.DOESNT_CONNECT
                continue
            await ws.send(json.dumps(
                {"machine_id": self.cfg['machine_id'],
                "token": sec.get_access_token(self.cfg).decode('ascii')}
            ))
            resp = json.loads(await ws.recv())
            if resp['status'] == "err":
                if resp['code'] == 903:
                    self.logger("auth failed, code 903, wrong auth data")
                    self.logger("will idle offline")
                    self.state = WsState.FAILED_AUTHDATA
                    return
                else:
                    self.logger(f"auth failed, code: {resp['code']}  , reconnect in 5 secs")
                    self.state = WsState.FAILED
                    await asyncio.sleep(5)
                    self.logger("reconnect")
                    self.state = WsState.DOESNT_CONNECT
                    continue
            self.logger("auth success")
            self.cfg = sec.set_token(self.cfg, resp['data']['token'])
            self.update_config()
            self.logger("config updated")
            self.state = WsState.READY
            async for msg in ws:
                self.state = WsState.MESSAGE
                self.msg.append(json.loads(msg))

    def run_wbs(self):
        asyncio.run(self.wbs_runner())

    def read(self):
        if len(self.msg) == 1: self.state = WsState.READY
        return self.msg.pop(0)

if __name__ == "__main__":
    from pfand_types import Logger
    logger = Logger()
    #run_wbs(json.load(open("Client/pfand_configs.json")), logger)