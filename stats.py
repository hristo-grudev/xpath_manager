import sqlite3
import config


def fetch_user_stats(user, user2=''):
    con = sqlite3.connect(config.db_path)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    stats = {
        'title_xpath': {},
        'pubdate_xpath': {},
        'author_xpath': {},
        'body_xpath': {},
    }
    cursor.execute("SELECT title_xpath, pubdate_xpath, author_xpath, body_xpath FROM log WHERE user=? OR user=?", (user, user2))
    results = cursor.fetchall()
    stat_columns = ['title_xpath', 'pubdate_xpath', 'author_xpath', 'body_xpath']
    for column in stat_columns:
        for entry in results:
            if entry[column] and entry[column] in stats[column]:
                stats[column][entry[column]] += 1
            else:
                stats[column][entry[column]] = 1

    for key in stats.keys():
        stats[key] = sorted(stats[key].items(), key=lambda x: x[1], reverse=True)[:20]

    lines = [f'\n{user}\n']
    for key in stats.keys():
        lines.append(f'\n{key}:\n')
        for xpath in stats[key]:
            lines.append(f'{xpath[0]}: {xpath[1]}\n')

    with open('stats.txt', 'a') as file:
        file.writelines(lines)
        file.close()


if __name__ == "__main__":
    with open('stats.txt', 'w') as f:
        f.close()

    fetch_user_stats(user="Daniel")
    fetch_user_stats(user="Simeon")
    fetch_user_stats(user="Hristo", user2="Bat Icho")
