import datetime
import socket
import re

from reverend.thomas import Bayes

HOST = 'irc.freenode.net'
PORT = 6667
USERNAME = 'El_bot'
I = 'JJ-bot'  # Goes into ~JJ-bot@yourprovidername.com
DESCRIPT = "HomeMade Bot by jeromej"

ROOM = '#put_your_channelname_here'

welcome_msg = 'sup bros?'  # Or False


# Teaches El_bot to detect when English messages are sent to answer to them "Midnight!" (inside joke)
translations = {
	'french': (
		'La souris est rentrée dans son trou.',
		'Il me faut plus de phrases en francais !',
		'Ok tu es prêt mon grand :)',
		'Je ne sais pas si je viendrai demain.',		
	),
	'english': (
		'My tailor is rich.',
		'Does anyone know?',
		'I do not plan to update my website soon.',
		'What about English then?',
		'After killing processing using up all your RAM on Linux (Firefox!!), move processes off of swap.',
		'please can you tell me what time is it',
		'Hacker Random Gif',
	),
}

# 1st January 1
last_midnight = datetime.datetime(1,1,1)

def safeprint(*args, **kwargs):
	""" Allows for printing in the terminal without crashing. Very basic """
	
	try:
		print(*args, **kwargs)
	except UnicodeEncodeError:
		print('Can\'t print that!')


def sendcmd(socket, msg):
	socket.send((msg+'\r\n').encode('utf-8'))

def sendmsg(socket, msg, to=ROOM):
	sendcmd(socket, 'PRIVMSG {} :{}'.format(to, msg))

def teach_guesser(guesser, translations):
	for lang, translation_list in translations.items():
		for translation in translation_list:
			# Ex: guesser.train('french', 'Je ne sais pas si je viendrai demain.'.lower())
			guesser.train(lang, translation)
	
	return guesser

guesser = Bayes()
guesser = teach_guesser(guesser, translations)

try:
	readbuffer = ''
	
	s = socket.socket()
	s.connect((HOST, PORT))
	
	sendcmd(s, 'NICK {}'.format(USERNAME))
	sendcmd(s, 'USER {} {} bla :{}'.format(I, HOST, DESCRIPT))
	sendcmd(s, 'JOIN {}'.format(ROOM))
	
	if welcome_msg:
		sendcmd(s, 'PRIVMSG {} :{}'.format(ROOM, welcome_msg))
	
	while 42:
		## Manual input ##
		# Sadly freezes the listening,
		# thus preventing to answer the PING request.
		#
		# # req = input('> ')
		req = ''
		
		if req:
			print('Sending "{}"'.format(req))
			sendcmd(s, req)
			
			continue
		
		new = s.recv(4096).decode('utf-8')
		
		if new:
			safeprint(new)
		
		readbuffer = readbuffer + new
		temp = str.split(readbuffer, '\n')
		readbuffer = temp.pop()
		
		for line in temp:
			line = str.rstrip(line)
			line = str.split(line)
			
			safeprint(' '.join(line))
			
			if line[0] == 'PING':
				sendcmd(s, 'PONG {}'.format(line[1]))
				print('PONG!')
			elif line[1] == 'PRIVMSG' and line[2] == ROOM:
				# Ex: :username!idthing PRIVMSG lghs :My message
				
				sender = line[0].split('!')[0][1:]
				msg = ' '.join(line[3:])[1:].rstrip()
				
				safeprint('{sender}: {msg}'.format(sender=sender, msg=msg))
				
				if msg.lower() == 'Ok {}, you ready?'.format(USERNAME).lower():
					print('Yes I am!')
					sendmsg(s, 'Yes I am!')
				elif re.match('^{}[:,] '.format(re.escape(USERNAME)), msg):
					msg = msg[len(USERNAME + ': '):]

					if msg.lower() == 'How old are you?'.lower():
						r = 'I\'m {} seconds old!'.format(
							int((datetime.datetime.now() - datetime.datetime(2016, 3, 30, 1, 16, 52)).total_seconds())
						)
						print(r)
						sendmsg(s, r)
				else:
					# guess = guesser.guess(msg[len(USERNAME + ': '):].lower())
					guess = guesser.guess(msg.lower())
					
					print(guess)
					
					if len(guess) == 1:
						lang, accuracy = guess[0]
						lang = lang.title()
						accuracy = accuracy*100
						
						if accuracy > 70:
							# sendmsg(s, 'I\'d say this is {} ({:.2f} %)'.format(lang, accuracy))
							
							if lang == 'English':
								if (datetime.datetime.now() - last_midnight).total_seconds() > 60 * 15:
									sendmsg(s, 'Midnight!')
									last_midnight = datetime.datetime.now()
						else:
							# sendmsg(s, 'I think this is {} ({:.2f} %'.format(lang, accuracy))
							pass
					else:
						# sendmsg(s, 'I\'m not sure what that is… ( {} )'.format(guess))
						pass
except KeyboardInterrupt:
	sendmsg(s, 'Bye bye~')
	s.close()
