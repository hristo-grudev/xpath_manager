import sqlite3
from datetime import datetime


def sync(db_from_path, db_to_path):
    def sync_new(db_from_path, db_to_path):
        db_from = sqlite3.connect(db_from_path)
        cur_from = db_from.cursor()

        db_to = sqlite3.connect(db_to_path)
        cur_to = db_to.cursor()

        ids_from = [item_id[0] for item_id in cur_from.execute("SELECT id FROM log").fetchall()]
        ids_to = [item_id[0] for item_id in cur_to.execute("SELECT id FROM log").fetchall()]

        ids_to_add = []
        for item_id in ids_from:
            if item_id not in ids_to:
                ids_to_add.append(item_id)

        if not ids_to_add:
            return

        full_items_to_add = []
        for item_id in ids_to_add:
            full_items_to_add.append(cur_from.execute("SELECT * FROM log WHERE id=?", (item_id,)).fetchone())
        for full_item in full_items_to_add:
            cur_to.execute("INSERT INTO log VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", full_item)
            print(f"Added entry {full_item[0]}")

        db_to.commit()
        db_to.close()
        db_from.close()

    def sync_updated(db_from_path, db_to_path):
        def array_to_dict(array):
            final_dict = {}
            for item in array:
                final_dict[item['id']] = {
                    'date': datetime.strptime(item['date'], '%d-%b-%Y %H:%M:%S')
                }
            return final_dict

        db_from_row = sqlite3.connect(db_from_path)
        db_from_row.row_factory = sqlite3.Row
        cur_from_row = db_from_row.cursor()

        db_to_row = sqlite3.connect(db_to_path)
        db_to_row.row_factory = sqlite3.Row
        cur_to_row = db_to_row.cursor()

        json_from = cur_from_row.execute("SELECT id,date FROM log").fetchall()
        json_to = cur_to_row.execute("SELECT id, date FROM log").fetchall()
        dict_to = array_to_dict(json_to)
        dict_from = array_to_dict(json_from)

        for item_id in dict_from.keys():
            if dict_from[item_id]['date'] > dict_to[item_id]['date']:
                new = cur_from_row.execute("SELECT * FROM log WHERE id=?", (item_id,)).fetchone()
                cur_to_row.execute("UPDATE log SET date=?, start_urls=?, menu_xpath=?, articles_xpath=?, title_xpath=?, pubdate_xpath=?, "
                                   "date_order=?, author_xpath=?,body_xpath=?, settings=?, domain=?, name=?, status=?, projects=?, botname=?,"
                                   " full_json=?, user=? WHERE id=?",
                                   (new['date'], new['start_urls'], new['menu_xpath'], new['articles_xpath'], new['title_xpath'], new['pubdate_xpath'], new['date_order'],
                                    new['author_xpath'], new['body_xpath'], new['settings'], new['domain'], new['name'], new['status'],
                                    new['projects'], new['botname'], new['full_json'], new['user'], item_id))
                print(f"Updated entry {item_id}")

        db_to_row.commit()
        db_to_row.close()
        db_from_row.close()

    print("Merging..")
    sync_new(db_from_path, db_to_path)
    sync_updated(db_from_path, db_to_path)
    print("Merged.")


if __name__ == "__main__":
    db1 = input("Database to pull from:")
    db2 = input("Database to insert into:")
    sync(db_from_path=db1, db_to_path=db2)
