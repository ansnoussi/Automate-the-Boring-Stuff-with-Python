from flask import Flask, request, Response, abort, send_from_directory
from selenium import webdriver
import sqlite3
import uuid

app = Flask(__name__)

conn = sqlite3.connect("screenshots.sqlite")
c = conn.cursor()

# Create DB Table if necessary
c.execute('CREATE TABLE IF NOT EXISTS screenshots (id INTEGER PRIMARY KEY AUTOINCREMENT, url STRING, filename STRING, ip STRING, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
conn.commit()


@app.route('/get_screenshot', methods=['GET'])
def get_screenshot():
    url = request.args.get('url')

    if url is None:
        return abort(400)

    c.execute("SELECT * FROM screenshots WHERE url = ? AND time>=datetime('now', '-1 Hour') ORDER BY time DESC", (url,))
    results = c.fetchall()

    if len(results) == 0:
        driver = webdriver.PhantomJS() # or add to your PATH
        driver.set_window_size(1024, 768) # optional
        driver.get(url)

        filename = "{}.png".format(uuid.uuid4())
        status = driver.save_screenshot("screenshots/{}".format(filename))
        driver.quit()

        if status is not True:
            return "Error generating capture", 404

        c.execute("INSERT INTO screenshots(url, filename, ip) VALUES(?, ?, ?)", (url, filename, request.remote_addr))
        conn.commit()
      else:
        filename = results[0][2]
        
    return send_from_directory("screenshots", filename)