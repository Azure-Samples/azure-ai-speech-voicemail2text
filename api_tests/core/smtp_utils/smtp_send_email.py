import ssl
from aiosmtplib import SMTP
from api_tests.core.config_utils import get_config_value


def create_ssl_context():
    ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.load_cert_chain(certfile='certs/client/certificate.pem', keyfile='certs/client/private_key.pem')
    ssl_context.load_verify_locations(cafile='../etc/certs/certificate.pem')
    return ssl_context


async def send_email(sender_email:str, receiver_email:str, message):
    smtp_server = get_config_value('smtptest', 'smtp_server_url')
    smtp_port = get_config_value('smtptest', 'smtp_server_port')
    ssl_context = create_ssl_context()
    smtp = SMTP(hostname=smtp_server, port=smtp_port, tls_context=ssl_context, start_tls=True)
    await smtp.connect()
    response = await smtp.send_message(message, sender=sender_email, recipients=receiver_email)
    await smtp.quit()

    print(f"Acknowledgement after sending mail: {response}")

    return smtp.hostname,smtp.port,response
