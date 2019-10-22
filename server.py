import pprint
from wsgiref import simple_server
import json
import falcon

import config


class EchoResource(object):
    def on_get(self, req, res):
        pprint.pprint(req)

    def on_post(self, req, res):
        payload = json.loads(req.params['payload'])
        pprint.pprint(payload)


class GithubEventHandler(object):
    def on_post(self, req, res):
        pprint.pprint(req.media)


app = falcon.API()

echo = EchoResource()
gevents = GithubEventHandler()

app.add_route('/', echo)
app.add_route('/event_handler', gevents)

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', config.PORT, app)
    print(f'Ready to receive requests on {config.PORT}')
    httpd.serve_forever()
