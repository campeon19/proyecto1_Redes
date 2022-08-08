import logging
from getpass import getpass
from argparse import ArgumentParser
import asyncio

import slixmpp

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class SendMsg(slixmpp.ClientXMPP):
    def __init__(self, jid, password, to, message):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.to = to
        self.message = message
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

        self.send_message(mto=self.to,
                          mbody=self.message, mtype='chat')
        self.disconnect()

    # def send_msg(self, to, message):
    #     self.send_message(mto=to,
    #                       mbody=message, mtype='chat')
    #     self.disconnect()


class GetListContacts(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        contactos = []
        roster = self.roster
        for jid in roster:
            contactos.append(jid)

        # for contact in self.roster.__getattribute__('items'):
        #     print(contact)
        self.disconnect()

        for x in range(0, 10):
            print("")
        print("Lista de contactos:")
        for contact in contactos:
            print(contact)


def menu():
    print("""
    1. Send message
    2. Get list contacts
    3. Disconnect from server
    """)


if __name__ == '__main__':
    # parser = ArgumentParser()
    # parser.add_argument('-j', '--jid', dest='jid', required=True, help='JID')
    # parser.add_argument('-p', '--password', dest='password',
    #                     required=True, help='Password')
    # parser.add_argument("-q", "--quiet", help="set logging to ERROR",
    #                     action="store_const", dest="loglevel",
    #                     const=logging.ERROR, default=logging.INFO)
    # parser.add_argument("-d", "--debug", help="set logging to DEBUG",
    #                     action="store_const", dest="loglevel",
    #                     const=logging.DEBUG, default=logging.INFO)
    # parser.add_argument("-t", "--to", dest="to",
    #                     help="JID to send the message to")
    # parser.add_argument("-m", "--message", dest="message",
    #                     help="message to send")

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    print('Bienvenido al chat usando el protocolo xmpp')
    # usuario = input('Ingrese su usuario completo: ')
    # password = input('Ingrese su contraseña: ')

    usuario = 'christianp@alumchat.fun'
    password = getpass('Ingrese su contraseña: ')

    # client = SendMsg(usuario, password)
    # client.register_plugin('xep_0030')  # Service Discovery
    # client.register_plugin('xep_0199')  # XMPP Ping
    # client.connect()
    # client.process(forever=False)

    menu()
    opcion = input('Ingrese una opcion: ')
    while opcion != '3':
        if opcion == '1':
            to = input('Ingrese el destinatario: ')
            msg = input('Ingrese el mensaje: ')
            # client.send_msg(to, msg)
            client = SendMsg(usuario, password, to, msg)
            client.register_plugin('xep_0030')  # Service Discovery
            client.register_plugin('xep_0199')  # XMPP Ping
            # client.disconnect()
            client.connect()
            client.process(forever=False)
        elif opcion == '2':
            client = GetListContacts(usuario, password)
            client.register_plugin('xep_0030')  # Service Discovery
            client.register_plugin('xep_0199')  # XMPP Ping
            client.connect()
            client.process(forever=False)

        menu()
        # client.disconnect()
        opcion = input('Ingrese una opcion: ')

    client.disconnect()

    print("Client disconnected.")
    exit(0)
