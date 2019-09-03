import sqlite3
import json
import os
from urllib.parse import urlparse


db_name = 'ads'


def create_table():
        db = sqlite3.connect("ads.db")
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS ads (id INTEGER ,images text, ad_text text)')
        db.commit()
        db.close()


def save_ad(ad):
        db = sqlite3.connect("ads.db")
        cursor = db.cursor()
        cursor.execute('INSERT INTO ads (id, images, ad_text) VALUES (?, ?, ?)', (ad.message_id, ad.text, json.dumps(ad.album)))
        db.commit()
        db.close()


def delete_ad(ad):
        db = sqlite3.connect("ads.db")
        cursor = db.cursor()
        cursor.execute('DELETE FROM ads WHERE id=?', (ad.message_id,))
        db.commit()
        db.close()


def get_ad(ad):
        db = sqlite3.connect("ads.db")
        cursor = db.cursor()
        cursor.execute('SELECT * FROM ads WHERE id =?', (ad.message_id,))
        data = cursor.fetchall()
        db.close()
        return data