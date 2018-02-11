#!flask/bin/python
from app import app
import os


if 'FLASK_APP' not in os.environ:
    os.environ['FLASK_APP'] = 'dices.py'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5027, debug=True)

