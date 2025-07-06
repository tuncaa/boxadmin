import sqlite3
from flask import g
import os

DATABASE = 'boxadmin.db'

def get_db():
    """Get database connection."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database with required tables."""
    db = get_db()
    
    # Create boxes table
    db.execute('''
        CREATE TABLE IF NOT EXISTS boxes (
            box_id INTEGER PRIMARY KEY AUTOINCREMENT,
            box_name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Create items table
    db.execute('''
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            box_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            img_url TEXT,
            FOREIGN KEY (box_id) REFERENCES boxes (box_id)
        )
    ''')
    
    db.commit()

def get_boxes():
    """Get all boxes from database."""
    db = get_db()
    return db.execute('SELECT * FROM boxes ORDER BY box_name').fetchall()

def get_box(box_id):
    """Get a specific box by ID."""
    db = get_db()
    return db.execute('SELECT * FROM boxes WHERE box_id = ?', (box_id,)).fetchone()

def get_items_by_box(box_id):
    """Get all items for a specific box."""
    db = get_db()
    return db.execute('SELECT * FROM items WHERE box_id = ? ORDER BY item_name', (box_id,)).fetchall()

def add_box(box_name, description, status='active'):
    """Add a new box to the database."""
    db = get_db()
    db.execute('INSERT INTO boxes (box_name, description, status) VALUES (?, ?, ?)',
               (box_name, description, status))
    db.commit()

def add_item(box_id, item_name, description, status='active', img_url=''):
    """Add a new item to the database."""
    db = get_db()
    db.execute('INSERT INTO items (box_id, item_name, description, status, img_url) VALUES (?, ?, ?, ?, ?)',
               (box_id, item_name, description, status, img_url))
    db.commit()