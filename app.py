import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

DATABASE = 'boxadmin.db'

def get_db_connection():
    """データベース接続を取得"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """データベースとテーブルを初期化"""
    conn = get_db_connection()
    
    # boxesテーブル作成
    conn.execute('''
        CREATE TABLE IF NOT EXISTS boxes (
            box_id INTEGER PRIMARY KEY AUTOINCREMENT,
            box_name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # itemsテーブル作成
    conn.execute('''
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
    
    # サンプルデータを挿入（テーブルが空の場合のみ）
    box_count = conn.execute('SELECT COUNT(*) FROM boxes').fetchone()[0]
    if box_count == 0:
        # サンプルボックス
        conn.execute('''
            INSERT INTO boxes (box_name, description, status) VALUES 
            ('キッチン収納', 'キッチン用品を収納するボックス', 'active'),
            ('リビング収納', 'リビング用品を収納するボックス', 'active'),
            ('寝室収納', '寝室用品を収納するボックス', 'active')
        ''')
        
        # サンプルアイテム
        conn.execute('''
            INSERT INTO items (box_id, item_name, description, status, img_url) VALUES 
            (1, '包丁', 'キッチン用包丁', 'active', ''),
            (1, 'フライパン', '中型フライパン', 'active', ''),
            (1, '調味料セット', '塩、コショウ、醤油など', 'active', ''),
            (2, 'リモコン', 'テレビ用リモコン', 'active', ''),
            (2, 'クッション', 'ソファ用クッション', 'active', ''),
            (3, '枕', '快眠用枕', 'active', ''),
            (3, 'アラーム時計', '目覚まし時計', 'active', '')
        ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """メイン画面：ボックス一覧を表示"""
    conn = get_db_connection()
    boxes = conn.execute('SELECT * FROM boxes WHERE status = "active" ORDER BY box_name').fetchall()
    conn.close()
    return render_template('index.html', boxes=boxes)

@app.route('/box/<int:box_id>')
def box_items(box_id):
    """指定されたボックス内のアイテム一覧を表示"""
    conn = get_db_connection()
    box = conn.execute('SELECT * FROM boxes WHERE box_id = ? AND status = "active"', (box_id,)).fetchone()
    if box is None:
        flash('ボックスが見つかりません')
        return redirect(url_for('index'))
    
    items = conn.execute(
        'SELECT * FROM items WHERE box_id = ? AND status = "active" ORDER BY item_name', 
        (box_id,)
    ).fetchall()
    conn.close()
    return render_template('box_items.html', box=box, items=items)

@app.route('/admin')
def admin():
    """管理画面"""
    return render_template('admin.html')

@app.route('/admin/add_box', methods=['GET', 'POST'])
def add_box():
    """ボックス追加画面"""
    if request.method == 'POST':
        box_name = request.form['box_name']
        description = request.form['description']
        
        if box_name:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO boxes (box_name, description, status) VALUES (?, ?, ?)',
                (box_name, description, 'active')
            )
            conn.commit()
            conn.close()
            flash('ボックスが追加されました')
            return redirect(url_for('admin'))
        else:
            flash('ボックス名は必須です')
    
    return render_template('add_box.html')

@app.route('/admin/add_item', methods=['GET', 'POST'])
def add_item():
    """アイテム追加画面"""
    conn = get_db_connection()
    boxes = conn.execute('SELECT * FROM boxes WHERE status = "active" ORDER BY box_name').fetchall()
    
    if request.method == 'POST':
        box_id = request.form['box_id']
        item_name = request.form['item_name']
        description = request.form['description']
        img_url = request.form['img_url']
        
        if box_id and item_name:
            conn.execute(
                'INSERT INTO items (box_id, item_name, description, status, img_url) VALUES (?, ?, ?, ?, ?)',
                (box_id, item_name, description, 'active', img_url)
            )
            conn.commit()
            conn.close()
            flash('アイテムが追加されました')
            return redirect(url_for('admin'))
        else:
            flash('ボックスとアイテム名は必須です')
    
    conn.close()
    return render_template('add_item.html', boxes=boxes)

if __name__ == '__main__':
    # データベース初期化
    init_db()
    # アプリケーション起動
    app.run(debug=True, host='0.0.0.0', port=5000)