import os
import asyncio
import ssl
import base64
from email.utils import formatdate
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from aiosmtplib import SMTP
from datetime import datetime, timezone

def create_ssl_context():
    ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.load_cert_chain(certfile='etc/certs/verizon_client/certificate.pem', keyfile='etc/certs/verizon_client/private_key.pem')
    ssl_context.load_verify_locations(cafile='etc/certs/certificate.pem')
    return ssl_context

def create_input_parameters(subject,language,x_voice_write,delivery_to):
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%a, %d %b %Y %H:%M:%S %z")
    input_parameters = {
        "subject" : subject,
        "x-cns-language" : language,
        "x-cns-voice-write" : x_voice_write,
        "delivered-to" : delivery_to,
        "message_id" : "20230519004356-epsnortheurope02-4130-91405",
        "reply_to" : "replyto@msft.com",
        "current_time" : date_str,
        "x-cns-interface-version" : "12",
        "from" : "19960596111",
        "content_type" : "Multipart/voice-message",
        "date": formatdate()
    }
    return input_parameters

def create_email_message_object(input_parameters):

    subject = 'Email with Multiple Audio Attachments'

    message = MIMEMultipart()
    message['From'] = 'abcde12345'
    message['To'] = 'verizon-us-comverse@verizon-us.nuancevm.co'
    message['Subject'] = subject

    message.add_header("Message-Id", input_parameters["message_id"])
    message.add_header("Reply-To", input_parameters["reply_to"])
    message.add_header("Delivery-date", input_parameters["current_time"])
    message.add_header("X-CNS-Interface-Version", input_parameters["x-cns-interface-version"])
    message.add_header("X-CNS-Voice-Writer" , input_parameters["x-cns-voice-write"])
    message.add_header("X-CNS-Language", input_parameters["x-cns-language"])
    message.add_header("Subject", input_parameters["subject"])
    message.add_header("Delivered-To", input_parameters["delivered-to"])
    message.add_header("From", input_parameters["from"])
    message.add_header("Content-Type", input_parameters["content_type"])
    message.add_header("Date", input_parameters["date"])
    return message

def create_file_attachments(attachment_files, message):
    # Attach the files
    for attachment_file in attachment_files:
        with open(attachment_file, 'rb') as f:
            attachment = MIMEBase('application', 'octet-stream')
            content = str(base64.encodebytes(f.read()), 'ascii')
            content_bytes = content.encode('ascii')
            attachment.set_payload(content_bytes)
            attachment.add_header('Content-Disposition', 'attachment', filename=attachment_file.split('/')[-1])
            attachment.add_header('Content-Transfer-Encoding', 'base64')
            message.attach(attachment)

async def send_email_with_multiple_audio_attachments(input_parameters):
    smtp_server = '127.0.0.1'
    smtp_port = 9443

    # Attachment files
    attachment_files = [
        "etc/audio/sample-audio-en-US-short.wav"
    ]

    mail_from = 'serviceABC@voicewriter1.messaging.Verizon.com'
    rcpt_to = 'verizon-us-comverse@verizon-us.nuancevm.com'

     # Create the email message
    message = create_email_message_object(input_parameters)
    #Attach files
    create_file_attachments(attachment_files,message)
    ssl_context = create_ssl_context()
    # Send the email
    smtp_client = SMTP(hostname=smtp_server, port=smtp_port, tls_context=ssl_context, start_tls=True)
    async with smtp_client:
        print(f'smtp email server connected successfully : {smtp_client.hostname}:{smtp_client.port}')
        return_tuple = await smtp_client.send_message(message, sender=mail_from, recipients=rcpt_to)
        print(f'return code: {return_tuple[1]}')


##Following methods used for send a request with different input of lanaguage and subject
async def send_email_with_lanuage_en_US_and_subject():
    input_param = create_input_parameters("Voice Audio email","en-US","true","19886066392")
    await send_email_with_multiple_audio_attachments(input_param)

async def send_email_with_lanuage_en_US_and_subject_PVVM_FTWM_English():
    input_param = create_input_parameters("PVVM-FTWM-English","en-US","true","19886066392")
    await send_email_with_multiple_audio_attachments(input_param)

async def send_email_with_lanuage_es_MX_and_subject_PVVM_FTWM_English():
    input_param = create_input_parameters("PVVM-FTWM-English","es-MX","true","19886066392")
    await send_email_with_multiple_audio_attachments(input_param)

async def send_email_with_lanuage_es_US_and_subject_PVVM_FTWM_English():
    input_param = create_input_parameters("PVVM-FTWM-English","es-US","true","19886066392")
    await send_email_with_multiple_audio_attachments(input_param)

async def send_email_with_lanuage_en_US_and_subject_PVVM_FTEM_English():
    input_param = create_input_parameters("PVVM_FTEM_English","en-US","true","19886066392")
    await send_email_with_multiple_audio_attachments(input_param)

async def send_email_with_lanuage_es_MX_and_subject_PVVM_FTEM_English():
    input_param = create_input_parameters("PVVM_FTEM_English","es-MX","true","19886066392")
    await send_email_with_multiple_audio_attachments(input_param)

async def send_email_with_lanuage_es_US_and_subject_PVVM_FTEM_English():
    input_param = create_input_parameters("PVVM_FTEM_English","es-US","true","19886066392")
    await send_email_with_multiple_audio_attachments(input_param)

async def send_email_with_lanuage_en_US_and_subject_PVVM_WM_English():
    input_param = create_input_parameters("PVVM-WM-English","en-US","true","19886066392")
    await send_email_with_multiple_audio_attachments(input_param)

async def send_email_with_lanuage_es_MX_and_subject_PVVM_WM_English():
    input_param = create_input_parameters("PVVM-WM-English","es-MX","true","19886066392")
    await send_email_with_multiple_audio_attachments(input_param)

async def send_email_with_lanuage_es_US_and_subject_PVVM_WM_English():
    input_param = create_input_parameters("PVVM-WM-English","es-US","true","19886066392")
    await send_email_with_multiple_audio_attachments(input_param)

async def send_email_with_delivery_to_blank():
    input_param = create_input_parameters("Voice Audio email","en-US","true","")
    await send_email_with_multiple_audio_attachments(input_param)

async def send_email_with_x_voice_write_as_false():
    input_param = create_input_parameters("Voice Audio email","en-US","false","19886066392")
    await send_email_with_multiple_audio_attachments(input_param)

# Run the email sending coroutine
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

##Whenever we want to run different scenarios, change the method name mentioned below.
asyncio.run(send_email_with_lanuage_en_US_and_subject())
print("Done")