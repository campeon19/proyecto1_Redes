
import logging
from getpass import getpass
from argparse import ArgumentParser
import asyncio
import xmpp
import os

import slixmpp
from slixmpp.exceptions import IqError, IqTimeout

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

        self.disconnect()

        for x in range(0, 10):
            print("")
        print("Lista de contactos:")
        for contact in contactos:
            print(contact)
        print(roster)


class MCRoom(slixmpp.ClientXMPP):
    def __init__(self, jid, password, room, message, nick):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.room = room
        self.msg = message
        self.nick = nick
        self.add_event_handler("session_start", self.start)
        # self.add_event_handler("groupchat_message", self.muc_message)
        # self.add_event_handler("muc::%s::got_online" % self.room,
        #                        self.muc_online)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        await self.plugin['xep_0045'].join_muc_wait(self.room,
                                                    self.nick,
                                                    )

        self.send_message(mto=self.room,
                          mbody=self.msg, mtype='groupchat')

    # def muc_message(self, msg):
    #     self.send_message(mto="babamayu@conference.alumchat.fun",
    #                       mbody=self.msg, mtype='groupchat')

    # def muc_online(self, presence):
    #     if presence['muc']['nick'] != self.nick:
    #         print("%s has come online" % presence['muc']['nick'])


class AddnewContact(slixmpp.ClientXMPP):
    def __init__(self, jid, password, name):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.name = name
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        # self.register_plugin('xep_0100')
        self.send_presence(pto=self.name, pstatus=None,
                           ptype='subscribe', pfrom=self.jid)
        self.disconnect()


class GetContactInfo(slixmpp.ClientXMPP):
    def __init__(self, jid, password, contact):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.contact = contact
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0077')
        self.register_plugin('xep_0199')
        self.register_plugin('xep_0054')
        contactos = []
        roster = self.client_roster
        for jid in roster:
            contactos.append(jid)
        if self.contact in contactos:
            for x in range(0, 10):
                print("")
            print("El contacto existe")
            print("Mostrando información del contacto: " + self.contact)
            print(roster[self.contact])
            # for key, value in roster[self.contact].items():
            #     print(key, value)
            for x in range(0, 10):
                print("")
        else:
            print("El contacto no existe")

        self.disconnect()


class DeleteAccount(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0077')
        self.register_plugin('xep_0199')
        request = self.Iq()
        request['type'] = 'set'
        request['from'] = self.boundjid.bare
        request['register']['remove'] = True
        try:
            request.send(True)
        except IqError as e:
            print('Error al eliminar cuenta: %s' % e.iq['error'])
            self.disconnect()
        except IqTimeout:
            print('Error al eliminar cuenta: timeout')
            self.disconnect()


class ChangeStatus(slixmpp.ClientXMPP):
    def __init__(self, jid, password, status, status_msg):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.status = status
        self.status_msg = status_msg
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        self.send_presence(pshow=self.status, pstatus=self.status_msg)
        await self.get_roster()
        print("Status changed to: %s" % self.status)
        print("Status message: %s" % self.status_msg)
        # self.disconnect()


class GetNotifications(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("presence_available", self.presence_available)
        self.add_event_handler("presence_unavailable",
                               self.presence_unavailable)
        self.add_event_handler("presence_subscribe", self.presence_subscribe)
        self.add_event_handler("presence_subscribed", self.presence_subscribed)
        self.add_event_handler("presence_unsubscribed",
                               self.presence_unsubscribed)
        self.add_event_handler("groupchat_message", self.groupchat_message)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print("%s says: %s" % (msg['from'], msg['body']))

    def presence_available(self, presence):
        print("%s is available" % presence['from'])

    def presence_unavailable(self, presence):
        print("%s is unavailable" % presence['from'])

    def presence_subscribe(self, presence):
        print("%s wants to subscribe to you" % presence['from'])
        self.send_presence(pto=presence['from'], ptype='subscribed')
        self.send_presence(pto=presence['from'], ptype='subscribe')

    def presence_subscribed(self, presence):
        print("%s is subscribed to you" % presence['from'])

    def presence_unsubscribed(self, presence):
        print("%s is unsubscribed from you" % presence['from'])

    def groupchat_message(self, msg):
        print("%s in %s says: %s" % (msg['mucnick'], msg['from'], msg['body']))


class SendFile(slixmpp.ClientXMPP):
    def __init__(self, jid, password, to, file):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.to = to
        self.file = file
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        self.register_plugin('xep_0066')

        iq = self.Iq()
        iq['type'] = 'set'
        iq['to'] = self.to
        iq['si']['profile'] = 'http://jabber.org/protocol/si/profile/file-transfer'
        iq['si']['file']['name'] = self.file
        iq['si']['file']['size'] = os.stat(self.file).st_size
        iq['si']['feature'] = {'var': 'http://jabber.org/protocol/feature-neg'}
        iq['si']['feature']['x']['field'] = {
            'var': 'stream-method', 'value': 'http://jabber.org/protocol/bytestreams'}
        iq['si']['feature']['x']['field'] = {
            'var': 'stream-method', 'value': 'http://jabber.org/protocol/ibb'}

        self.disconnect()


def createNewAccount(jid, password):
    print("Creating new account...")
    account_user = xmpp.JID(jid)
    account_password = password
    client = xmpp.Client(account_user.getDomain(), debug=[])
    client.connect()
    if xmpp.features.register(client, account_user.getDomain(), {'username': account_user.getNode(), 'password': account_password}):
        print("Account created")
    else:
        print("Account not created")


def menu_inicial():
    print("""
    1. Create new account
    2. Login
    """)


def menu():
    print("""
    1. Send message
    2. Get list contacts
    3. Get status from contacts
    4. Send message in group chat
    5. Get contact details
    6. Delete account
    7. Add new contact
    8. Change status
    9. Receive notifications
    10. Disconnect from server
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

    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(levelname)-8s %(message)s')

    # logging.basicConfig(level=args.loglevel,
    #                     format='%(levelname)-8s %(message)s')

    print("""
            ______ _                           _     _       
            | ___ (_)                         (_)   | |      
            | |_/ /_  ___ _ ____   _____ _ __  _  __| | ___  
            | ___ \ |/ _ \ '_ \ \ / / _ \ '_ \| |/ _` |/ _ \ 
            | |_/ / |  __/ | | \ V /  __/ | | | | (_| | (_) |
            \____/|_|\___|_| |_|\_/ \___|_| |_|_|\__,_|\___/ 
                                                            
                                                            
    """)

    print('Bienvenido al chat usando el protocolo xmpp')

    menu_inicial()
    op = input("Seleccione una opción: ")
    if op == "1":
        jid = input("Introduzca su usuario con el dominio incluido: ")
        password = input("Introduzca su contraseña: ")
        ver = input('Introduzca nuevamente su contraseña: ')
        if password == ver:
            createNewAccount(jid, password)
        else:
            print("Las contraseñas no coinciden")
            print('Cuenta no creada')

    print('Inicio de sesion')
    usuario = 'chrisbot4@alumchat.fun'
    password = getpass('Ingrese su contraseña: ')

    # usuario = 'christianp@alumchat.fun'

    menu()
    opcion = input('Ingrese una opcion: ')
    while opcion != '10':
        if opcion == '1':
            # to = input('Ingrese el destinatario: ')
            to = 'christianp@alumchat.fun'
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
        elif opcion == '3':
            pass
        elif opcion == '4':
            room = input('Ingrese el nombre del sala: ')
            msg = input('Ingrese el mensaje: ')
            nick = input('Ingrese su nick: ')
            client = MCRoom(usuario, password, room, msg, nick)
            client.register_plugin('xep_0030')  # Service Discovery
            client.register_plugin('xep_0199')  # XMPP Ping
            client.register_plugin('xep_0045')  # Multi-User Chat
            client.connect()
            client.process(timeout=10)
            client.disconnect()
        elif opcion == '5':
            contact = input('Ingrese el nombre del contacto: ')
            client = GetContactInfo(usuario, password, contact)
            client.connect()
            client.process(forever=False)
        elif opcion == '6':
            print('Borrando cuenta')
            print("Esta seguro de borrar su cuenta?")
            q = input('Ingrese "si" para borrar: ')
            if q == 'si':
                client = DeleteAccount(usuario, password)
                client.register_plugin('xep_0030')  # Service Discovery
                client.register_plugin('xep_0199')  # XMPP Ping
                client.register_plugin('xep_0077')  # In-Band Registration
                client.register_plugin('xep_0100')
                client.connect()
                client.process(forever=False)
                print('Cuenta borrada')
                break
            else:
                print('Cancelado')
        elif opcion == '7':
            print('Agregando nuevo contacto')
            name = input('Ingrese el nombre: ')
            client = AddnewContact(usuario, password, name)
            client.register_plugin('xep_0030')  # Service Discovery
            client.register_plugin('xep_0199')  # XMPP Ping
            client.register_plugin('xep_0077')  # In-Band Registration
            client.register_plugin('xep_0100')
            client.connect()
            client.process(forever=False)
        elif opcion == '8':
            print('Cambiando estado')
            status = input(
                'Ingrese su estado:\n away \n chat \n dnd \n xa \n ')
            status_msg = input('Ingrese su mensaje de estado: ')
            client = ChangeStatus(usuario, password, status, status_msg)
            client.register_plugin('xep_0030')  # Service Discovery
            client.register_plugin('xep_0199')  # XMPP Ping
            client.connect()
            client.process(timeout=20)
            # client.disconnect()
        elif opcion == '9':
            print('Encender notificaciones')
            tiempo = input(
                'Ingrese el tiempo en segundos que desea activar las notificaciones: ')
            if tiempo.isdigit():
                client = GetNotifications(usuario, password)
                client.register_plugin('xep_0030')  # Service Discovery
                client.register_plugin('xep_0199')  # XMPP Ping
                client.register_plugin('xep_0045')  # Multi-User Chat
                client.connect()
                client.process(timeout=int(tiempo))
            else:
                print('Lo que ingreso no es un numero. Cancelando')

        menu()
        # client.disconnect()
        opcion = input('Ingrese una opcion: ')

    # client.disconnect()
    print("Client disconnected.")
    exit(0)
