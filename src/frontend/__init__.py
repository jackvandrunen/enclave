from stream420 import stream, launch
from bottle import route, static_file, error


def start(f2bq, b2fq, host='localhost', port=7775):
    out_stream, in_stream = stream('/stream', f2bq.put, b2fq)

    @route('/')
    def main():
        return static_file('main.html', root='./views', mimetype='text/html')

    @route('/<path:path>')
    def servef(path):
        return static_file(path, root='./views')

    @error(500)
    @error(404)
    @error(401)
    def errormsg(err):
        return 'Error!'

    return launch(host=host, port=port)
