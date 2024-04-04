from website import create_app
from flask_socketio import SocketIO
from flask_moment import Moment
from flask import render_template

import os

socket,app = create_app()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(threaded=True,port=os.getenv("PORT"), host='0.0.0.0')
    #socket.run(app,debug=True)