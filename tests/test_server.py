import http.client,json,threading,unittest
from http.server import ThreadingHTTPServer
from server import Handler

class LocalBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.port=cls.server.server_address[1]
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close()
    def request(self,method,path,body=None,headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=3)
        conn.request(method,path,body=body,headers=headers or {});response=conn.getresponse()
        result=(response.status,response.read(),dict(response.getheaders()));conn.close();return result
    def test_ui_serves_with_script_and_frame_restrictions(self):
        status,body,headers=self.request('GET','/')
        self.assertEqual(status,200);self.assertIn(b'PauseDock',body)
        self.assertIn("frame-ancestors 'none'",headers['Content-Security-Policy'])
    def test_foreign_browser_origin_cannot_send_notes(self):
        status,_,_=self.request('POST','/api/park','{}',{'Origin':'https://unrelated.example','Content-Type':'application/json'})
        self.assertEqual(status,403)
    def test_untrusted_host_rejected(self):
        status,_,_=self.request('GET','/',headers={'Host':'unrelated.example'})
        self.assertEqual(status,403)
    def test_unknown_static_paths_do_not_expose_files(self):
        status,_,_=self.request('GET','/../core.py');self.assertEqual(status,404)
    def test_bad_or_excessive_notes_rejected_before_inference(self):
        for body,status in [('{}',400),(json.dumps({'notes':'only one note'}),422),('x'*30001,413)]:
            actual,_,_=self.request('POST','/api/park',body,{'Content-Type':'application/json'})
            self.assertEqual(actual,status)

if __name__=='__main__':unittest.main()
