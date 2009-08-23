import xmpp
from msettings import gmailUser, gmailPassword

def sendMessage(recipientList, message):
    jid = xmpp.protocol.JID(gmailUser)
    cl = xmpp.Client('gmail.com', debug=[])
    cl.connect(server=('talk.google.com',5223))
    cl.auth(jid.getNode(), gmailPassword, sasl=0)
    cl.sendInitPresence(requestRoster=0)
    roster = cl.getRoster()
    for recipient in recipientList:
        if recipient.endswith('gmail.com'):
            cl.send(xmpp.protocol.Message(recipient, message))
    cl.disconnect()
    
