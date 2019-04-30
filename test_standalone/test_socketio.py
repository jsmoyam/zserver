
from flask import Flask#, request
from flask_classful import FlaskView
from flask_socketio import SocketIO, Namespace, emit

app = Flask(__name__)
socketio = SocketIO(app)

quotes = [
    "A noble spirit embiggens the smallest man! ~ Jebediah Springfield",
    "If there is a way to do it better... find it. ~ Thomas Edison",
    "No one knows what he can do till he tries. ~ Publilius Syrus"
]

class QuotesView(FlaskView):

    class MyCustomNamespace(Namespace):
        def on_connect(self):
            print('[namespace] connect')
            pass

        def on_disconnect(self):
            print('[namespace] disconnect')
            pass

        def on_my_event(self, data):
            print('[namespace] my event: {}'.format(data))
            emit('my_response', data)

        def on_my_personal_event(self, data):
            print('[namespace] my personal event: {}'.format(data))
            emit('my_personal_response', data)

    socketio.on_namespace(MyCustomNamespace('/test'))

    def index(self):
        return "<br>".join(quotes)
QuotesView.register(app)


# class MyCustomNamespace(Namespace):
#     def on_connect(self):
#         print('[namespace] connect')
#         pass
#
#     def on_disconnect(self):
#         print('[namespace] disconnect')
#         pass
#
#     def on_my_event(self, data):
#         print('[namespace] my event')
#         emit('my_response', data)
#
#     def on_my_personal_event(self, data):
#         print('[namespace] my personal event')
#         emit('my_personal_response', data)
#
# socketio.on_namespace(MyCustomNamespace('/test'))


# @app.route('/getquotes')
# def getquotes():
#     return "".join(quotes)
#
# @socketio.on('my event', namespace='/test')
# def test_message1(message):
#     print('received [my event] {}'.format(message))
#     emit('my response', {'data': 'Respuesta a [my event]'})
#
# @socketio.on('my broadcast event', namespace='/test')
# def test_message2(message):
#     print('received [my broadcast event] {}'.format(message))
#     emit('my response', {'data': 'Respuesta a [my broadcast event]'}, broadcast=True)
#
# @socketio.on('connect', namespace='/test')
# def test_connect():
#     emit('my response', {'data': 'Connected client'})
#
# @socketio.on('disconnect', namespace='/test')
# def test_disconnect():
#     print('Client disconnected')

# socketio.on_event('my event', test_message1, namespace='/test')


if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app, host='0.0.0.0')