from security import *
from utility import *
import json

async def machine_user_get(machine_id, data, users, tokens, info):
    if users.find_one(data['filter']):
        return "ok", encrypt(machine_id, tokens, json.dumps(no_object_id(users.find_one(data['filter'])))).decode("utf-8")
    
async def machine_user_set(machine_id, data, users, tokens, info):
    new_data = json.loads(decrypt(machine_id, tokens, bytes(data['new_data'], 'utf-8')))
    if users.find_one(data['filter']):
        users.find_one_and_replace(data['filter'], new_data)
    else:
        user = new_data
        user['user_id'] = info['last_user_id'] + 1
        info['last_user_id'] += 1
    return "ok", "ok"


OPS = {
    "machine.user.get": {
        "fields": ["filter"],
        "func": machine_user_get
    },
    "machine.user.set": {
        "fields": ["filter", "new_data"],
        "func": machine_user_set
    }
}