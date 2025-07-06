from flask import Flask, render_template, request, redirect, url_for, g
from database import init_db, close_db, get_boxes, get_box, get_items_by_box, add_box, add_item

app = Flask(__name__)

@app.teardown_appcontext
def close_db_on_teardown(error):
    """Close database connection when application context ends."""
    close_db(error)

@app.route('/')
def index():
    """Main page showing list of boxes."""
    boxes = get_boxes()
    return render_template('index.html', boxes=boxes)

@app.route('/box/<int:box_id>')
def box_detail(box_id):
    """Show items in a specific box."""
    box = get_box(box_id)
    if not box:
        return "Box not found", 404
    
    items = get_items_by_box(box_id)
    return render_template('box_detail.html', box=box, items=items)

@app.route('/add_box', methods=['GET', 'POST'])
def add_box_route():
    """Add a new box."""
    if request.method == 'POST':
        box_name = request.form['box_name']
        description = request.form['description']
        status = request.form.get('status', 'active')
        
        add_box(box_name, description, status)
        return redirect(url_for('index'))
    
    return render_template('add_box.html')

@app.route('/add_item', methods=['GET', 'POST'])
def add_item_route():
    """Add a new item."""
    if request.method == 'POST':
        box_id = request.form['box_id']
        item_name = request.form['item_name']
        description = request.form['description']
        status = request.form.get('status', 'active')
        img_url = request.form.get('img_url', '')
        
        add_item(box_id, item_name, description, status, img_url)
        return redirect(url_for('box_detail', box_id=box_id))
    
    boxes = get_boxes()
    return render_template('add_item.html', boxes=boxes)

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)