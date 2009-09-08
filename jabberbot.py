import xmpp
from msettings import gmailUser, gmailPassword, statusMessage
from bot import bot

class jabberbot(bot):
    def __init__(self):
        self.botType = 'jabber'
        self.VALID_DOMAINS = ['gmail.com', 'googlemail.com']
        
    def sendMessage(self, recipientList, message):
        """
        Method to send jabber messages to a recipient list.
        """
        jid = xmpp.protocol.JID(gmailUser)
        cl = xmpp.Client(jid.getDomain(), debug=[])
        cl.connect(server=('talk.google.com', 5223))
        cl.auth(jid.getNode(), gmailPassword, sasl=0)
        cl.sendInitPresence(requestRoster=0)
        pres=xmpp.Presence(priority=5, show="available", status=statusMessage)
        cl.send(pres)
        roster = cl.getRoster()
        for recipient in recipientList:
            if not self.isValid(recipient):
                continue
            userJid = xmpp.protocol.JID(recipient)
            roster.Subscribe(userJid)
            roster.Authorize(userJid.getNode())
            cl.send(xmpp.protocol.Message(recipient, message))
        cl.disconnect()

