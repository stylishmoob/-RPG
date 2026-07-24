import sqlite3
from flask import Flask
import os
import io
import csv

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")











def get_status_up_rules():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT master_categories.id,
                master_categories.category_name,
                statuses.status_name,
                statuses.status_type,
                status_up_rules.gain_per_hours,
                 
        FROM status_up_rules
        JOIN master_categories
        ON status_up_rules.category_id=master_categories.id
        JOIN statuses
        ON status_up_rules.status_id=statuses.id
        WHERE master_categories.is_active=1 """)
    
    status_up_rules=cur.fetchall()
    
    conn.close()
    return status_up_rules







def get_user_master_categories():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("""
        SELECT id ,
                category_name
        FROM master_categories
        WHERE is_active=1""")
    
    user_master_categories=cur.fetchall()

    conn.close()
    return user_master_categories










  

       

















    





























        



    
def get_users():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT id,user_name,user_level,is_admin
        FROM users
                """)
    
    users=cur.fetchall()

    conn.close()
    return users












    




    


    






    