import json
from xmlrpc.client import ProtocolError
import requests
from twisted.python import failure

from twisted.internet import reactor
from quarry.types.uuid import UUID
from quarry.net.proxy import UpstreamFactory, Upstream, DownstreamFactory, Downstream, Bridge
from quarry.net import auth, crypto
from quarry.net.server import ServerFactory, ServerProtocol
from twisted.internet import reactor

from lognk import log
from colorama import Fore, Back, Style

import configparser
import sys
import os
from booltool import toBool


ini = configparser.ConfigParser()
ini['HomuraMC'] = {'server_ip': '0.0.0.0','port': 25565,'motd': 'A Minecraft Server','token': "<How To Token Get: https://kqzz.github.io/mc-bearer-token/>",'eula': False}
if os.path.isfile("./Homura.ini") == False:
	with open('Homura.ini', 'w') as configfile:
		# 指定したconfigファイルを書き込み
		ini.write(configfile)

ini.read('./Homura.ini', 'UTF-8')
if toBool(ini['HomuraMC']['eula']) != True:
	log(Fore.RED + "You do not agree with the eula! The eula can be read at https://aka.ms/MinecraftEULA and to agree, set the eula to True in Homura.ini." + Fore.RESET,Fore.RED + "[error]" + Fore.RESET)
	print("Press Key to Continue...")
	input()
	sys.exit()
elif (ini['HomuraMC']['token'] == "<How To Token Get: https://kqzz.github.io/mc-bearer-token/>") or (ini['HomuraMC']['token'] == ""):
	log(Fore.RED+"Your token has not been set! Please see how to get a token ( https://kqzz.github.io/mc-bearer-token/ ) to set it up!" + Fore.RESET,Fore.RED+"[error]" + Fore.RESET)
	print("Press Key to Continue...")
	input()
	sys.exit()

class MyDownstream(Downstream):
	def packet_login_encryption_response(self, buff):
		if self.login_expecting != 1:
			raise ProtocolError("Out-of-order login")

		# 1.7.x
		if self.protocol_version <= 5:
			def unpack_array(b): return b.read(b.unpack('h'))
		# 1.8.x
		else:
			def unpack_array(b): return b.read(b.unpack_varint(max_bits=16))
		log(f"{self.display_name} is trying to connect!")
		log(f"{self.display_name}'s protocol version: {self.protocol_version}")

		p_shared_secret = unpack_array(buff)
		p_verify_token = unpack_array(buff)

		shared_secret = crypto.decrypt_secret(
			self.factory.keypair,
			p_shared_secret)

		verify_token = crypto.decrypt_secret(
			self.factory.keypair,
			p_verify_token)

		self.login_expecting = None

		if verify_token != self.verify_token:
			raise ProtocolError("Verify token incorrect")

		# enable encryption
		self.cipher.enable(shared_secret)
		self.logger.debug("Encryption enabled")

		# make digest
		digest = crypto.make_digest(
			self.server_id.encode('ascii'),
			shared_secret,
			self.factory.public_key)

		# do auth
		remote_host = None

		# deferred = auth.has_joined(
		#	 self.factory.auth_timeout,
		#	 digest,
		#	 self.display_name,
		#	 remote_host)
		# deferred.addCallbacks(self.auth_ok, self.auth_failed)

		r = requests.get('https://sessionserver.mojang.com/session/minecraft/hasJoined',
						 params={'username': self.display_name, 'serverId': digest, 'ip': remote_host})

		if r.status_code == 200:
			self.auth_ok(r.json())
			log(f"{self.display_name} is Connected!")
		else:
			self.auth_failed(failure.Failure(
				auth.AuthException('invalid', 'invalid session')))


class MyBridge(Bridge):
	def make_profile(self):
		"""
		Support online mode
		"""

		# follow: https://kqzz.github.io/mc-bearer-token/

		accessToken = ini['HomuraMC']['token']

		url = "https://api.minecraftservices.com/minecraft/profile"
		headers = {'Authorization': 'Bearer ' + accessToken}
		response = requests.request("GET", url, headers=headers)
		result = response.json()
		myUuid = UUID.from_hex(result['id'])
		myUsername = result['name']
		return auth.Profile('(skip)', accessToken, myUsername, myUuid)


class MyDownstreamFactory(DownstreamFactory):
	global ini
	protocol = MyDownstream
	bridge_class = MyBridge
	motd = ini["HomuraMC"]["motd"]
	

def main():

	# Create factory
	factory = MyDownstreamFactory()

	# Listen
	factory.listen(ini['HomuraMC']['server_ip'],int(ini['HomuraMC']['port']))
	reactor.run()


if __name__ == "__main__":
	log("Homura v0.0.1 is Finished Loading!")
	main()
