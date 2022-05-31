import sqlite3


def extract_metadata(twi):
    data = {}

    data['text'] = twi['text']
    data['id'] = twi['id']
    data['created_at'] = twi['created_at']
    data['user_id'] = twi['user']['id']
    data['user_name'] = twi['user']['name']
    data['user_screen_name'] = twi['user']['screen_name']
    data['user_description'] = twi['user']['description']

    return data


def init_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS favorite_tweets(
        id integer primary key, 
        text text, 
        created_at text, 
        user_id integer, 
        user_name text,
        user_screen_name text, 
        user_description text
        )''')
    conn.commit()
    conn.close()


def insert_twi(twi, db_path):
    twi = extract_metadata(twi)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # check if tweet already exists
    cur.execute('SELECT id FROM favorite_tweets WHERE id=?', (twi['id'],))
    if cur.fetchone() is not None:
        pass
    else:
        # insert tweet
        cur.execute('INSERT INTO favorite_tweets VALUES (?,?,?,?,?,?,?)',
                    (twi['id'],
                     twi['text'],
                     twi['created_at'],
                     twi['user_id'],
                     twi['user_name'],
                     twi['user_screen_name'],
                     twi['user_description']))
        conn.commit()

    conn.close()
