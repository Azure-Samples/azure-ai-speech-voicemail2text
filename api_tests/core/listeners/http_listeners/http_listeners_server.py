import http.server
import ssl
import threading
from api_tests.core.listeners.http_listeners.request_handler import RequestHandler

class HTTPListenerServer:
    stop_server_flag = False
    def create_ssl_context(self):
        ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_SERVER)
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.load_cert_chain(certfile='certs/v2tic_listener.crt', keyfile='certs/v2tic_listener.key')
        ssl_context.load_verify_locations(cafile='../etc/certs/client/certificate.pem')
        return ssl_context

    def start_listener(self,host,port):
        # Create an HTTP server object with custom request handler
        http_server = http.server.HTTPServer((host, port), RequestHandler)
        ssl_context:ssl.SSLContext = self.create_ssl_context()
        http_server.socket = ssl_context.wrap_socket(http_server.socket, server_side=True)

        # Start the server
        server_thread = threading.Thread(target=http_server.serve_forever)
        server_thread.start()
        print(f"============Test HTTP Listener started on host {host} and port {port}============")
        # Wait for the user to stop the server
        try:
            while not HTTPListenerServer.stop_server_flag:
                pass
        except KeyboardInterrupt:
            pass

        # Stop the server gracefully
        http_server.shutdown()
        http_server.server_close()

    def stop_listener(self):
        # Set the stop_server_flag to True to stop the server
        HTTPListenerServer.stop_server_flag = True

    def reset_stop_server_flag(self):
        # Set the stop_server_flag to True to stop the server
        HTTPListenerServer.stop_server_flag = False
