import sqlite3
from flask import g, current_app
from PIL import Image
import io
import logging



def init_db(app):
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config['DATABASE'])
    return db

def close_connection(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_images_and_labels(user_id, data_id):
    logging.basicConfig(filename='train.log', level=logging.DEBUG)
    db = get_db()
    cursor = db.cursor()

    # Define the SQL query
    sql_query = """
        SELECT labels.image_id, labels.label, images.image_data
        FROM images
        INNER JOIN labels ON images.id = labels.image_id
        WHERE images.data_id = ? AND labels.data_id = ?
        AND images.user_id = ? AND labels.user_id = ?;
    """

    # Execute the SQL query
    cursor.execute(sql_query, (data_id, data_id, user_id, user_id))


    # Fetch all the results
    results = cursor.fetchall()

    

    # Define a list to hold the data
    image_data_list = []

    # Process the results
    for row in results:
        # Extract data from the row
        image_name, label, image_data = row
        # logging.debug(f'this is results: {results}')

        
        # Convert BLOB data to image
        image = Image.open(io.BytesIO(image_data))
        # logging.debug(f'this is row: {row}')
        # Create a dictionary to hold the image data
        image_data_dict = {
            'image_id': image_name,
            'label': label,
            'image': image  # Store the image object directly
        }
        
        # Append the dictionary to the list
        image_data_list.append(image_data_dict)

    # Return the structured data
    return image_data_list

def get_image_id(filename, user_id, data_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id FROM images WHERE filename = ? AND user_id = ? AND data_id = ?', (filename, user_id, data_id))
    result = cursor.fetchone()
    if result:
        return result[0]  # Return the image_id
    else:
        print("Image with filename '{}' for user_id '{}' and data_id '{}' not found.".format(filename, user_id, data_id))
        return None

    
def save_image_to_db(user_id, data_id, filename, image_data):
    db = get_db()
    db.execute('INSERT INTO images (user_id, data_id, filename, image_data) VALUES (?, ?, ?, ?)', (user_id, data_id, filename, image_data))
    db.commit()

def save_labels_to_db(user_id, data_id, image_name, label):
    image_id = get_image_id(image_name, user_id, data_id)
    if image_id is not None:
        db = get_db()
        # Insert into labels table with image_id and label
        db.execute('INSERT INTO labels (user_id, data_id, image_id, label) VALUES (?, ?, ?, ?)', (user_id, data_id, image_id, label))
        db.commit()

def save_train_to_db(trained_model_file_path, loss, accuracy, optimizer_type, lr, momentum, epochs, training_time_seconds, training_time_minutes):
    db = get_db()
    db.execute('INSERT INTO trains (trained_model_file_path, loss, accuracy, optimizer_type, lr, momentum, epochs, train_time_secs, train_time_mins) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
               (trained_model_file_path, loss, accuracy, optimizer_type, lr, momentum, epochs, training_time_seconds, training_time_minutes))
    db.commit()

def save_model_to_db(upload_path, user_id):
    db = get_db()
    db.execute('INSERT INTO models (model_path, user_id) VALUES (?, ?)', [upload_path, user_id])
    db.commit()

