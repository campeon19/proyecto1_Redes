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


def menu():
    print("""
    1. Send message
    2. Disconnect from server
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
    usuario = input('Ingrese su usuario completo: ')
    password = input('Ingrese su contraseña: ')

    # client = SendMsg(usuario, password)
    # client.register_plugin('xep_0030')  # Service Discovery
    # client.register_plugin('xep_0199')  # XMPP Ping

    menu()
    opcion = input('Ingrese una opcion: ')
    while opcion != '2':
        if opcion == '1':
            to = input('Ingrese el destinatario: ')
            msg = input('Ingrese el mensaje: ')
            client = SendMsg(usuario, password, to, msg)
            client.register_plugin('xep_0030')  # Service Discovery
            client.register_plugin('xep_0199')  # XMPP Ping
            # client.disconnect()
            client.connect()
            client.process(forever=False)
        menu()
        # client.disconnect()
        opcion = input('Ingrese una opcion: ')

    # client.disconnect()

    print("Client disconnected.")
    exit(0)
