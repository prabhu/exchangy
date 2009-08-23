import os
import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.Encoders import encode_base64
from msettings import *

def sendMail(subject, recipientList, text, html, *attachmentFilePaths):
    """
    Method to send email using gmail.
    """
    global gmailUser, gmailPassword
    msg = MIMEMultipart()
    msg['From'] = gmailUser    
    msg['Subject'] = subject

    msgAlternative = MIMEMultipart('alternative')
    msg.attach(msgAlternative)
    if text:
        msgText = MIMEText(text)
        msgAlternative.attach(msgText)
    if html:
        msgText = MIMEText(html, 'html')
        msgAlternative.attach(msgText)

    for attachmentFilePath in attachmentFilePaths:
        msg.attach(handleAttachment(attachmentFilePath))
    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmailUser, gmailPassword)
    for recipient in recipientList:
        if not recipient:
            continue
        msg['To'] = recipient
        mailServer.sendmail(gmailUser, recipient, msg.as_string())
    mailServer.close()
    print('Sent email to %s' % recipient)

def handleAttachment(attachmentFilePath):
    """
    Method to handle attachment
    """
    contentType, encoding = mimetypes.guess_type(attachmentFilePath)
    if contentType is None or encoding is not None:
        contentType = 'application/octet-stream'
    mainType, subType = contentType.split('/', 1)
    file = open(attachmentFilePath, 'rb')
    fileText = file.read()
    if mainType == 'text':
        attachment = MIMEText(fileText)
    elif mainType == 'message':
        attachment = email.message_from_file(file)
    elif mainType == 'image':
        attachment = MIMEImage(file.read(),_subType=subType)
    elif mainType == 'audio':
        attachment = MIMEAudio(file.read(),_subType=subType)
    else:
        attachment = MIMEBase(mainType, subType)
    attachment.set_payload(fileText)
    encode_base64(attachment)
    file.close()
    attachment.add_header('Content-Disposition', 'attachment',   filename=os.path.basename(attachmentFilePath))
    return attachment
