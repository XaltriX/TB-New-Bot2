
import motor.motor_asyncio
import logging
from config import ADMINS, DB_URL, DB_NAME

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
database = dbclient[DB_NAME]

user_data = database['users']
is_u_first = database['fst_time']
admin_data= database['admins']

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': {
            'is_verified': False,
            'verified_time': "",
            'verify_token': "",
            'link': ""
        }
    }

#users
async def present_user(user_id: int):
    found = await user_data.find_one({'_id': user_id})
    logging.info(f"{bool(found)}")
    return bool(found)

async def add_user(user_id: int):
    user = new_user(user_id)
    await user_data.insert_one(user)
    return
async def add_is_first(user_id: int):
    is_fst = await is_u_first.insert_one({'_id': user_id})
    return

async def is_first(user_id: int):
    is_f_fnd = is_u_first.find_one({'_id': user_id})
    logging.info(f"{bool(is_f_fnd)}")
    return bool(is_f_fnd)

async def del_is_first(user_id: int):
    del_fst = await is_u_first.delete_one({'_id': user_id})
    return


async def db_verify_status(user_id):
    user = await user_data.find_one({'_id': user_id})
    if user:
        return user.get('verify_status', default_verify)
    return default_verify

async def db_update_verify_status(user_id, verify):
    await user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})

async def full_userbase():
    user_docs = user_data.find()
    user_ids = [doc['_id'] async for doc in user_docs]
    return user_ids

async def del_user(user_id: int):
    await user_data.delete_one({'_id': user_id})
    return

#admins

async def present_admin(user_id: int):
    found = await admin_data.find_one({'_id': user_id})
    return bool(found)


async def add_admin(user_id: int):
    user = new_user(user_id)
    await admin_data.insert_one(user)
    ADMINS.append(int(user_id))
    return

async def del_admin(user_id: int):
    await admin_data.delete_one({'_id': user_id})
    ADMINS.remove(int(user_id))
    return

async def full_adminbase():
    user_docs = admin_data.find()
    user_ids = [int(doc['_id']) async for doc in user_docs]
    return user_ids