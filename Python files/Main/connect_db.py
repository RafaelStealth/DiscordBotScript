import pymysql


async def db_connect(query):
    # Conecte-se ao banco de dados
    conn = pymysql.connect(
        host="localhost",
        user="",
        password="",
        db="iron_bot_database"
    )

    # Crie um cursor
    cursor = conn.cursor()

    try:
        # Execute o comando para mostrar as tabelas
        cursor.execute(query)
        conn.commit()

        rows_affected = cursor.rowcount

        if cursor.rowcount > 0:
            print(f"\033[30:42m A query afetou {rows_affected} linha(s) \033[m")
        else:
            print("\033[0:30:41m Não houve nenhuma linha afetada pela query\033[m")

        # Recupere os resultados
        result = cursor.fetchall()
    except pymysql.err.ProgrammingError as error:
        print(f"A query falhou: {error}")

    cursor.close()
    conn.close()

    return result

