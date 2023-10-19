import connect_db


async def authorized_users_ia():
    resultquery = await connect_db.db_connect('SELECT user_id FROM authorized_users_ia;')
    list_id_bd = list()
    for user in resultquery:
        user_id_bd = list(user)
        list_id_bd.append(user_id_bd[0])
    return list_id_bd
