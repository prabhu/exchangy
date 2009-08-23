import xmpp
from msettings import gmailUser, gmailPassword

def sendMessage(recipientList, message):
    jid = xmpp.protocol.JID(gmailUser)
    cl = xmpp.Client(jid.getDomain(), debug=[])
    cl.connect(server=('talk.google.com', 5223))
    cl.auth(jid.getNode(), gmailPassword, sasl=0)
    cl.sendInitPresence(requestRoster=0)
    pres=xmpp.Presence(priority=5, show="available", status="Exchangy - The only Exchange Rates Bot.")
    cl.send(pres)
    roster = cl.getRoster()
    for recipient in recipientList:
        if not recipient:
            continue
        if recipient.endswith('gmail.com') or recipient.endswith('googlemail.com'):
            userJid = xmpp.protocol.JID(recipient)
            roster.Subscribe(userJid)
            roster.Authorize(userJid.getNode())
            cl.send(xmpp.protocol.Message(recipient, message))
    cl.disconnect()
    