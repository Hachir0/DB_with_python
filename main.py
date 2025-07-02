import psycopg2

con = psycopg2.connect(database="hw_5", user="postgres", password="postgres")


def create_db():
    with con.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS client(
                id SERIAL PRIMARY KEY,
                firstname VARCHAR(255),
                lastname VARCHAR(255),
                email VARCHAR(255)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS client_phones(
                id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES client(id) ON DELETE CASCADE,
                phone VARCHAR(255)
            );
        """)
        con.commit()
    print("База данных создана")


def add_client(firstname, lastname, email):
    with con.cursor() as cur:
        cur.execute("""
            INSERT INTO client(firstname, lastname, email)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (firstname, lastname, email))
        client_id = cur.fetchone()[0]
        con.commit()
    print(f"Клиент добавлен с ID = {client_id}")
    return client_id


def add_phone(client_id, phone):
    with con.cursor() as cur:
        cur.execute("""
            INSERT INTO client_phones(client_id, phone)
            VALUES (%s, %s);
        """, (client_id, phone))
        con.commit()
    print(f"Телефон добавлен для клиента {client_id}")


def change_client(client_id, firstname=None, lastname=None, email=None):
    with con.cursor() as cur:
        if firstname:
            cur.execute("UPDATE client SET firstname = %s WHERE id = %s", (firstname, client_id))
        if lastname:
            cur.execute("UPDATE client SET lastname = %s WHERE id = %s", (lastname, client_id))
        if email:
            cur.execute("UPDATE client SET email = %s WHERE id = %s", (email, client_id))
        con.commit()
    print("Клиент изменён")


def delete_phone(client_id, phone):
    with con.cursor() as cur:
        cur.execute("""
            DELETE FROM client_phones
            WHERE client_id = %s AND phone = %s;
        """, (client_id, phone))
        con.commit()
    print("Телефон удалён")


def delete_client(client_id):
    with con.cursor() as cur:
        cur.execute("DELETE FROM client WHERE id = %s", (client_id,))
        con.commit()
    print("Клиент удалён")


def find_client(firstname=None, lastname=None, email=None, phone=None):
    with con.cursor() as cur:
        query = """
            SELECT c.id, c.firstname, c.lastname, c.email, p.phone
            FROM client c
            LEFT JOIN client_phones p ON c.id = p.client_id
            WHERE TRUE
        """
        params = []
        if firstname:
            query += " AND c.firstname = %s"
            params.append(firstname)
        if lastname:
            query += " AND c.lastname = %s"
            params.append(lastname)
        if email:
            query += " AND c.email = %s"
            params.append(email)
        if phone:
            query += " AND p.phone = %s"
            params.append(phone)

        cur.execute(query, tuple(params))
        results = cur.fetchall()
        if results:
            print("Найденные клиенты:")
            for row in results:
                print(row)
        else:
            print("Клиенты не найдены")


# Пример использования
if __name__ == "__main__":
    create_db()

    # Добавляем клиентов
    id1 = add_client("Kamil", "Kulishev", "kamil@gmail.com")
    id2 = add_client("Anna", "Petrova", "anna@example.com")
    id3 = add_client("Ivan", "Sidorov", "ivan@example.com")

    # Добавляем номера
    add_phone(id1, "1234567890")
    add_phone(id1, "111222333")
    add_phone(id2, "999888777")

    # Изменяем данные клиента
    change_client(id3, firstname="Ivan", lastname="Smirnov", email="ivan.smirnov@example.com")

    # Удаляем один номер
    delete_phone(id1, "111222333")

    # Поиск по email
    find_client(email="ivan.smirnov@example.com")

    # Поиск по телефону
    find_client(phone="999888777")

    # Удаляем клиента
    delete_client(id2)

    # Поиск после удаления
    find_client(email="anna@example.com")