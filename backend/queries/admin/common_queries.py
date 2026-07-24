import sqlite3
from flask import Flask
import os
import csv
import io

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")


def insert_default_category_achievements(cur,category_id,category_name):
    DEFAULT_CATEGORY_ACHIEVEMENTS = [
    {"required_hours": 1,"title_name": "入門者",},
    {"required_hours": 10,"title_name": "見習い",},
    {"required_hours": 50,"title_name": "初級者",},
    {"required_hours": 100,"title_name": "熟練者",},
    {"required_hours": 500,"title_name": "達人",},
    {"required_hours": 1000,"title_name": "名人",},
    {"required_hours": 2000,"title_name": "極めし者",},
    {"required_hours": 3000,"title_name": "伝説",},
    ]

    for achievement in DEFAULT_CATEGORY_ACHIEVEMENTS:
        cur.execute("""
            INSERT INTO master_achievements (
                required_category_id,
                required_hours,
                achievement_name,
                title_name
            )
            VALUES(?,?,?,?)
            """,
            (  
                category_id,
                achievement["required_hours"],
                f"{category_name}{achievement['required_hours']}時間達成!",
                f"{category_name}{achievement['title_name']}",
            ),
        )