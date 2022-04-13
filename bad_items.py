import sqlite3

import config


def find_bad_items():
    con = sqlite3.connect(config.local_db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    id_name_tuples = cur.execute("SELECT name, domain, id, user, date FROM log WHERE status='Running'").fetchall()
    bad_items = []
    for item in id_name_tuples:
        if item['name'] not in item['domain']:
            bad_items.append(item)
    if bad_items:
        with open('bad items.txt', 'w') as f:
            f.write('Items with wrong name or domain\n')
            for item in bad_items:
                f.write(f'{item["id"]},{item["user"]},{item["date"]}\n')
            f.write('____________________________________________\n')
    bad_items = cur.execute("SELECT id, user, date FROM log WHERE status='Stopped' AND projects!=''").fetchall()
    if bad_items:
        with open('bad items.txt', 'a') as f:
            f.write('Stopped items with projects:\n')
            for item in bad_items:
                f.write(f'{item["id"]},{item["user"]},{item["date"]}\n')
            f.write('____________________________________________\n')

    bad_items = cur.execute("SELECT id, user, date FROM log WHERE status='Running' AND body_xpath=''").fetchall()
    if bad_items:
        with open('bad items.txt', 'a') as f:
            f.write('Items with no body:\n')
            for item in bad_items:
                f.write(f'{item["id"]},{item["user"]},{item["date"]}\n')
            f.write('____________________________________________\n')

    bad_items = cur.execute("SELECT id, user, date FROM log WHERE start_urls=''").fetchall()

    if bad_items:
        with open('bad items.txt', 'a') as f:
            f.write('Items with no URL:\n')
            for item in bad_items:
                f.write(f'{item["id"]},{item["user"]},{item["date"]}\n')
            f.write('____________________________________________\n')

    bad_items = cur.execute("SELECT id, user, date FROM log WHERE botname='siteshtml' AND articles_xpath='' AND status='Running'").fetchall()

    if bad_items:
        with open('bad items.txt', 'a') as f:
            f.write('Siteshtml items with not articles_xpath:\n')
            for item in bad_items:
                f.write(f'{item["id"]},{item["user"]},{item["date"]}\n')
            f.write('____________________________________________\n')

    bad_items = cur.execute("SELECT id, user, date FROM log WHERE botname='siteshtml' AND title_xpath='' AND status='Running'").fetchall()

    if bad_items:
        with open('bad items.txt', 'a') as f:
            f.write('Siteshtml items with no title_xpath:\n')
            for item in bad_items:
                f.write(f'{item["id"]},{item["user"]},{item["date"]}\n')
            f.write('____________________________________________\n')


if __name__ == '__main__':
    find_bad_items()
