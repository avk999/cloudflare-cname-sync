
# Empty line at top of the file simplifies helm template messing
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import logging
logging.basicConfig(level=logging.DEBUG)

DEST={
'kind': 'Service',
'apiVersion': 'v1',
'metadata': {
},
#  name: {prefix}-{name}
#  annotations:
#    external-dns.alpha.kubernetes.io/hostname: {name}
#    external-dns.alpha.kubernetes.io/ttl: "{ttl}"
'spec':{
  'type': 'ExternalName'}
}
#  externalName: {tunnel_id}.cfargotunnel.com'''

class Controller(BaseHTTPRequestHandler):

  def sync(self, parent):
    tunnel_id=os.environ.get('TUNNEL_ID')
    ttl=os.environ.get('TTL','30')
    prefix=os.environ.get('PREFIX')

    rules = parent.get("spec",{}).get("rules",[])
    logging.info(f"Processing parent {parent}")
    hosts=[x['host'] for x in rules]

    def processhost(h):
        logging.debug(f"processing host {h}")
        result={
            'kind': 'Service',
            'apiVersion': 'v1',
            'metadata': { },
            #  name: {prefix}-{name}
            #  annotations:
            #    external-dns.alpha.kubernetes.io/hostname: {name}
            #    external-dns.alpha.kubernetes.io/ttl: "{ttl}"
            'spec':{
              'type': 'ExternalName'}
            }
        result['metadata']['name']=h.replace('.','-')
        result['metadata']['annotations']={
             'external-dns.alpha.kubernetes.io/hostname': h,
             'external-dns.alpha.kubernetes.io/ttl':str(ttl)
        }
        result['spec']['externalName']=f"{tunnel_id}.cfargotunnel.com"
        return result
    attachments=[processhost(x) for x in hosts]
    labels={'created-by': 'external-service-generator'}
    annotations={}
    result= {'attachments': attachments, 'labels':labels, 'annotations':annotations}
    logging.info(f"result: {result}")
    return result



  def do_POST(self):
    # Serve the sync() function as a JSON webhook.
    observed = json.loads(self.rfile.read(int(self.headers.get("content-length"))))
    desired = self.sync(observed['object'])

    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.end_headers()
    logging.info(f"returning {json.dumps(desired)}")
    self.wfile.write(json.dumps(desired).encode())
logging.info(f"Starting")
HTTPServer(("", 80), Controller).serve_forever()
