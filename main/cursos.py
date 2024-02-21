import psycopg2


def deleteServiceByCursor(service_id)->None:
    conn = psycopg2.connect(dbname="main_db", host="localhost", user="ivan", password="123", port="5432")
    cursor = conn.cursor()
    query = f'UPDATE "Service" SET status = false WHERE id = {service_id};'
    cursor.execute(query)
    conn.commit()   # реальное выполнение команд sql1
    cursor.close()
    conn.close()