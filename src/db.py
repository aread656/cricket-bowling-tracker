import sqlite3 as sql
from delivery import Delivery

# define connection and cursor
connection = sql.connect('cricket_tracker.db')
cursor = connection.cursor()

def init_db():
    cursor.execute("PRAGMA foreign_keys = ON;") # enable foreign key constraints

    # create trajectories table
    create_trajectories_table = """CREATE TABLE IF NOT EXISTS
    trajectories(trajectory_id INTEGER PRIMARY KEY)"""
    cursor.execute(create_trajectories_table)
    create_trajectory_points_table = """CREATE TABLE IF NOT EXISTS 
    trajectory_points(trajectory_points_id INTEGER PRIMARY KEY,
    trajectory_id INTEGER,
    x REAL,
    y REAL,
    t INTEGER,
    FOREIGN KEY (trajectory_id) REFERENCES trajectories(trajectory_id))"""
    cursor.execute(create_trajectory_points_table)

    # create deliveries table
    create_deliveries_table = """CREATE TABLE IF NOT EXISTS
    deliveries(delivery_id INTEGER PRIMARY KEY, 
    trajectory_id INTEGER,
    path TEXT, 
    run_up INTEGER, 
    distance INTEGER, 
    speed FLOAT,
    FOREIGN KEY(trajectory_id) REFERENCES trajectories(trajectory_id))"""
    cursor.execute(create_deliveries_table)

    connection.commit()

def save_delivery_to_db(delivery:Delivery, path: str):

    cursor.execute("SELECT delivery_id,trajectory_id FROM deliveries WHERE path = ?", (path,))
    existing_record = cursor.fetchone()

    if existing_record is not None:
        delivery_id, trajectory_id = existing_record

        # update the delivery with new data
        cursor.execute("""UPDATE deliveries 
        SET run_up = ?, distance = ?, speed = ? WHERE delivery_id = ?""",
        (delivery.run_up,delivery.distance,delivery.speed, delivery_id),)

        # delete the old trajectory row
        cursor.execute("""DELETE FROM trajectory_points WHERE trajectory_id = ?""", (trajectory_id,))
    else:
        # create new trajectory record and set ID
        cursor.execute("INSERT INTO trajectories DEFAULT VALUES")
        trajectory_id = cursor.lastrowid

        # format & insert delivery values
        cursor.execute("""INSERT INTO deliveries 
        (trajectory_id, path, run_up, distance, speed) VALUES (?,?,?,?,?)""",
        (trajectory_id, path, delivery.run_up, delivery.distance, delivery.speed),)
        
    # format & insert trajectory points values
    points = [(trajectory_id, point[0][0], point[0][1], point[1])
              for point in delivery.trajectory]
    cursor.executemany("""INSERT INTO 
    trajectory_points (trajectory_id,x,y,t) 
    VALUES (?,?,?,?)""", points)
    
    connection.commit()