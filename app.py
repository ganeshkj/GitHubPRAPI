from flask import Flask
from urls import urls

app = Flask(__name__)

for i in urls():
    app.add_url_rule(i[0], i[1], i[2])

if __name__ == '__main__':
    app.run()

