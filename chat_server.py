import random
import time
from threading import Thread
import pickle
import msvcrt
import socket
import codecs
import sys
from chat_server import *

server_ip = '127.0.0.1'     # The IP of the server.
server_welcome_port = 9023  # The port the server will use.
timeout = 5                 # The "waiting" client buffer size of the welcome_socket.
buffer_size = 256           # The buffer size of the sending and receiving sockets.
welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # The socket everyone initially connects to.
input_handler = ''          # This will process console input to the server.
message_handler = ''        # This will maintain the message history and keep track of all printed/displayed messages.
user_handler = ''           # This will manage user information including usernames, login credentials, and user IDs.
client_handler = ''         # This will manage connection information and sockets.
file_handler = ''           # This will perform read/writes of the message history and user credentials.
communication_handler = ''  # This will process anything that requires sending or receiving to/from sockets.
continue_listening = True   # FUTURE: Used to clean shutdown.
continue_processing = True  # FUTURE: Used for clean shutdown.
continue_input = True       # FUTURE: Used for clean shutdown.
continue_validating = True  # FUTURE: Used for clean shutdown.
history_path = 'history.txt'# The location/file path of the saved history.
credentials_path = 'credentials.txt'    # The location/file path of the saved login credentials.
test_mode = False           # Run tests?

def main():
    if len(sys.argv) == 3:
        try:
            server_ip = str(sys.argv[1])
            server_welcome_port = int(sys.argv[2])
        except:
            server_ip = '127.0.0.1'
            server_welcome_port = 9023
    else:
        print 'usage: ./filename.py (ip | port)'
    initialize_handlers()
    thread_load_history = Thread(target=file_handler.read_message_history, args=()) # This thread will load the history into memory.
    thread_load_credentials = Thread(target=file_handler.read_user_credentials, args=()) # This thread will load the user credentials into memory.
    thread_load_history.start()
    thread_load_credentials.start()
    thread_load_history.join()
    thread_load_credentials.join()
    start_loops()   # Start all the main loops.


def initialize_handlers():
    global input_handler
    global message_handler
    global user_handler
    global client_handler
    global file_handler
    global communication_handler
    print 'Initializing handlers...'
    input_handler = InputHandler()
    message_handler = MessageHandler()
    user_handler = UserHandler()
    client_handler = ClientHandler()
    file_handler = FileHandler()
    communication_handler = CommunicationHandler()
    print 'Handlers initialized.'

def start_loops():
    print 'Starting all threads...'
    try:
        thread_welcome = Thread(target=client_handler.listen_for_connections, args=())  # This thread will constantly listen for/accept incoming connections.
        thread_push = Thread(target=communication_handler.push_new_messages, args=())   # This thread will constantly push new messages to the clients.
        thread_validate = Thread(target=client_handler.validate_all_sockets, args=())   # This thread will constantly check to make sure sockets are still alive.   
        thread_input = Thread(target=input_handler.process_server_input, args=())       # This thread will deal with gathering direct user input from the console.
        thread_welcome.start()
        thread_push.start()
        thread_validate.start()
        thread_input.start()
        print '...threads started.'
        if test_mode==True:
            run_tests()
    except:
        print 'ERROR: Problem starting threads.'
        
def run_tests(): #Disabled from access via program running - must be coded in.
    test_message_handler()
    test_nick_handler()
    
def get_time():
    cur_time = time.ctime()
    cur_time = time.strftime("%d/%b/%y - %H:%M:%S")
    return str(cur_time)

def get_user_handler():
    return user_handler

def get_client_handler():
    return client_handler

def get_message_handler():
    return message_handler

def test_message_handler():
        print 'Dumping messages...'
        message_handler.dump_messages()
        print '...messages dumped.'
        print 'Adding messages (an exchange between a Spartan and a Persian...'
        message_handler.process_command_msg(1412413, '/MSG This is blasphemy.', get_time())
        message_handler.process_command_msg(1412413, '/MSG This is madness!', get_time())
        message_handler.process_command_msg(1412411, '/MSG Madness?', get_time())
        message_handler.process_command_msg(1412411, '/MSG THIS', get_time())
        message_handler.process_command_msg(1412411, '/MSG IS', get_time())
        message_handler.process_command_msg(1412411, '/MSG SPARTAAAAAAAA!', get_time())
        message_handler.process_command_msg(1412411, '/MSG *KICK*', get_time())
        message_handler.process_command_msg(1412413, '/MSG AHHHHHHHHHHHHH', get_time())
        print '...messages added.'
        print 'Dumping messages (8 messages, 0-7)...'
        message_handler.dump_messages()
        print '...messages dumped.'
        print 'Attempting to obtian last twenty messages...'

def test_nick_handler():
        print 'User Tester 9000...'
        message_handler.set_message_history([])
        user_handler.process_command_nick(1414, '/NICK Gandalf whatawizard', get_time())
        message_handler.process_command_msg(1414, '/MSG YOU SHALL NOT PASS.', get_time())
        user_handler.process_command_nick(1413, '/NICK Gandalf b', get_time())
        user_handler.process_command_nick(1413, '/NICK Gandalf whatawizard', get_time())
        message_handler.process_command_msg(1413, '/MSG I guess I am stuck.', get_time())
        user_handler.process_command_nick(1413, '/NICK Balrog notawizard', get_time())
        message_handler.process_command_msg(1413, '/MSG Oh well - time to test for bugs!', get_time())
        
        user_handler.process_command_nick(1413, '/NICK lol', get_time())
        user_handler.process_command_nick(1413, '/NICK Balrog', get_time())
        user_handler.process_command_nick(1413, '/NICK Balrog notawizard', get_time())
        message_handler.dump_messages()
        
        
class InputHandler(object):
    save_credentials = '1'
    save_history = '2'
    quit_server = '9'
    
    def __init__(self):
        pass
    
    def process_server_input(self):
        print 'Press ' + self.save_credentials + ' to save user credentials.'
        print 'Press ' + self.save_history + ' to save message history.'
        user_input = ''
        while continue_input == True:
            try:
                if msvcrt.kbhit()==True:
                    user_input = user_input+msvcrt.getche()
                    if user_input == self.save_history:
                        thread_history_save = Thread(target=file_handler.write_message_history, args=())
                        thread_history_save.start()
                    elif user_input == self.save_credentials:
                        thread_credentials_save = Thread(target=file_handler.write_user_credentials, args=())
                        thread_credentials_save.start()
                    elif user_input == self.quit_server:
                        pass
                    user_input = ''
            except Exception, e:
                print 'ERROR: Unable to process input.'
                print e
                
class MessageHandler(object):
    message_history = []         # This list will store the message log.
    unused_message_id = 0         # This int keeps track of the internal ID used to order messages.
    #users = []
    last_pushed = 0

    def __init__(self):
        self.message_history = []
        self.unused_message_id = 0
        
# Process a request from a client to append a new message to the message history to display to other users.
    def process_command_msg(self, user_id, text):
        try:
            timestamp = get_time()
            username = user_handler.identify_user(user_id) # Identify the user with the given userID.
            message_to_append = timestamp + ' [' + username + ']: ' + text[5:]
            self.add_to_messages(message_to_append)
        except:
            print 'Unable to append message with (ID:' + str(self.get_unused_message_id()) + ' to message history.'

# Process a request from a client to retrieve the last 20 messages.
    def process_command_last(self, user_id, data):
        timestamp = get_time()
        last_twenty = []
        socket_to_send_to = client_handler.get_client_with(user_id)[0]
        if len(self.message_history)>=20:
            old_messages = self.message_history[-20:]
        else:
            old_messages = self.message_history
        for each in old_messages:
            last_twenty.append(each[1].strip())
        send_thread = Thread(target=communication_handler.send_till_done, args=(last_twenty, socket_to_send_to))
        send_thread.start()
        send_thread.join()

# Process a request from a client to receive the server's current status.
    def process_command_status(self, user_id, data):
        timestamp = get_time()
        status = []
        socket_to_send_to = client_handler.get_client_with(user_id)[0]
        try:
            users_keys = user_handler.users.keys()
            status.append(self.make_server_message('Server IP: ' + str(server_ip), get_time()))
            status.append(self.make_server_message('Server Port: ' + str(server_welcome_port), get_time()))
            status.append(self.make_server_message('Connected users: ' + str(len(users_keys)), get_time()))
            for each in users_keys:
                status.append(self.make_server_message(user_handler.users[each], get_time()))
            send_thread = Thread(target=communication_handler.send_till_done, args=(status, socket_to_send_to))
            send_thread.start()
            send_thread.join()
        except Exception, e:
            print 'Unable to return status to user ' + str(user_id) + '.'
            print e

# Post a message directly from the server into the message history (different formatting than usual messages)           
    def post_server_message(self, message, timestamp):
        print 'Posting server message...\n'
        server_message = self.make_server_message(message, timestamp)
        self.add_to_messages(server_message)
        
    def make_server_message(self, message, timestamp):
        return timestamp + ' ---SERVER---: ' + message
    
    def inc_message_id(self):
        self.unused_message_id=self.unused_message_id+1

    def add_to_messages(self, message):
        try:
            self.message_history.append((self.get_unused_message_id(), message))
            self.inc_message_id()
        except:
            print 'ERROR: Unable to append message (ID: ' + str(self.get_unused_message_id()) + ' to message history.'

    def get_unused_message_id(self):
        return self.unused_message_id
    
    def get_last_pushed(self):
        return self.last_pushed
    
    def set_last_pushed(self, new_last_pushed):
        self.last_pushed = new_last_pushed
        
    def set_unused_message_id(self, new_unused_message_id):
        self.unused_message_id = new_unused_message_id
        
    def get_message_history(self):
        return self.message_history
    
    def set_message_history(self, history_new):
        self.message_history = history_new
        
    def dump_messages(self):
        for each in self.message_history:
            print each


class UserHandler(object):
    users = {}      # Contain username information for all connected users. Key is the user_id.
    credentials = {}# Contain username and password combinations for all users. Key is the username.
    admins = {}     # FUTURE: Contain admin flags
    def __init__(self):
        self.users = {}
        
# Process nickname change requests from clients.
    def process_command_nick(self, user_id, message):
        timestamp = get_time()
        split_text = message.strip()
        split_text = split_text.split(' ')
        users_keys = self.users.keys()
        used = False
        if len(split_text)==3:
            username_old = self.identify_user(user_id)
            if split_text[1] in self.credentials:
                try:
                    if self.credentials[split_text[1]] == split_text[2]:
                        for each in users_keys:
                            if self.users[each] == split_text[1]:
                                used = True
                        if used==False:
                            self.users[user_id] = split_text[1]
                            message_handler.post_server_message(username_old + ' has changed name to ' + self.users[user_id] + '.', get_time())
                        else:
                            message_handler.post_server_message(username_old + ' failed to change name to ' + split_text[1] + ': name already in use.', get_time())
                    else:
                        message_handler.post_server_message(username_old + ' has failed to change name to ' + split_text[1] + ': incorrect password.', get_time())
                except:
                    pass
            else:
                self.credentials[split_text[1]] = split_text[2]
                self.users[user_id] = split_text[1]
                message_handler.post_server_message(username_old + ' has registered and changed name to ' + self.users[user_id] +'.', get_time())
# Retrieve the username associated with the user_id, or if it does not exist, create one.            
    def identify_user(self, user_id):
        username = 'Unknown'
        try:
            if user_id in self.users: #If the user has already been identified...
                username = self.users[user_id]
            else: #Else give the user a new unique name.
                username = 'StrangerDanger' + str(random.randint(0, 1000))
                while username in self.users==True: #Does this loop work? TODO: Check.
                    username = 'StrangerDanger' + str(random.randint(0, 1000)) 
                self.users[user_id] = username
        except:
            print 'Error identifying user with ID:', user_id
        return username
# Retrieve the user_id associated with the username.
    def reverse_identify_user(self, username):
        try:
            user_keys = self.users.keys()
            for each in user_keys:
                if self.users[keys]==username:
                    return each
        except Exception, e:
            print 'Unable to identify user ' + username + ' through username.'
            print e
        return ''
# Bookkeeping
    def remove_user_with_id(self, user_id):
        try:
            del self.users[user_id]
            print 'User with id ' + str(user_id) + ' successfully removed from active users list.'
        except Exception, e:
            print 'ERROR: Unable to delete user from active users list.'
            print e
            
    def create_random_id(self):
        random_id = random.randint(0, 1000)
        used_ids = client_handler.get_clients().keys()
        while random_id in used_ids==True:
            random_id = random.randint(0, 1000)
        return random_id


class CommunicationHandler(object):

    def __init__(self):
        pass
# Send the contents of the list to the socket.
    def send_till_done(self, send_this, socket):
        try:
            if len(send_this)>0:
                for each in send_this:
                    try:
                        socket.send(self.pad_this(each))
                    except Exception, e:
                        print 'ERROR: Unable to send padded message.'
                        print e
        except:
            print 'ERROR: Unable to send data to client.'
# Determine which messages are new and push them to all clients.            
    def push_new_messages(self):
        print 'Pushing new messages.\n'
        while True:
            if message_handler.get_last_pushed()!=message_handler.get_unused_message_id()-1:
                push_these = self.get_new_since_last_push()
                if len(push_these)>0:
                    sockets_to_send_to = []
                    clients_keys = client_handler.clients.keys()
                    for each in clients_keys:
                        try:
                            sockets_to_send_to.append(client_handler.clients[each][0])
                        except KeyError:
                            print 'ERROR: Found nonresponsive socket when pushing new messages.'
                    print '\nAttempting to push messages to ' + str(len(sockets_to_send_to)) + ' clients.'
                    for each in sockets_to_send_to:
                        try:
                            send_thread = Thread(target=self.send_till_done, args=(push_these, each))
                            send_thread.start()
                            send_thread.join()
                        except Exception, e:
                            print 'ERROR: Unable to push messages to client: ' + each + '.'
                            print e
                    print 'Finished processing all messages.\n'
                    message_handler.set_last_pushed(message_handler.get_unused_message_id()-1)
       

            
    def get_new_since_last_push(self):
        num = message_handler.get_last_pushed()+1
        message_list = []
        while num < message_handler.get_unused_message_id():
            message_list.append(message_handler.message_history[num][1])
            num = num+1
        message_handler.set_last_pushed(message_handler.get_unused_message_id()-1)
        return message_list

# Call the appropriate methods to handle the commands.           
    def process_input_old(self, socket, user_id):
        data = ''
        while continue_processing:
            try:
                data = socket.recv(buffer_size)
                if len(data)>0:
                    new_text = data.strip()
                    new_text = data.split(' ')
                    if len(new_text)>0:
                        command = new_text[0]
                        if command == '/MSG':
                            message_handler.process_command_msg(user_id, data, get_time())
                            print 'Processing /MSG from client', user_id, '.' 
                        elif command == '/NICK':
                            user_handler.process_command_nick(user_id, data, get_time())
                            print 'Processing /NICK from client', user_id, '.'
                        elif command == '/LAST':
                            message_handler.process_command_last(user_id, data, get_time())
                            print 'Processing /LAST from client', user_id, '.'
                        elif command == '/STATUS':
                            print 'Processing /STATUS from client', user_id, '.'
                            message_handler.process_command_status(user_id, data, get_time())
                data = ''
            except:
               pass # Nothing to process.
            
    def process_input(self, socket, user_id):
        data = ''
        # The functions variable holds the commands that the server can process.
        functions = {'/MSG': message_handler.process_command_msg,
                     '/NICK': user_handler.process_command_nick,
                     '/LAST': message_handler.process_command_last,
                     '/STATUS': message_handler.process_command_status}
        while continue_processing:
            try:
                data = socket.recv(buffer_size)
                if len(data)>0:
                    new_text = data.strip()
                    new_text = data.split(' ')
                    if len(new_text)>0:
                        command = new_text[0]
                        try:
                            func = functions.get(command)
                            if func != None:
                                print '\nProcessing ' + str(command) + ' from client ' + str(user_id) + '.'
                                func(user_id, data)
                                command = ''
                        except Exception, e:
                            print e
                data = ''
            except:
                pass

    
    def pad_this(self, message):
        message = message.strip()
        if len(message)<buffer_size:
            difference = buffer_size - len(message)
            padded_message = message + (' ' * difference)
            return padded_message
        elif len(message)==buffer_size:
            return message
        else:
            print 'ERROR: Message too long.'
            return ' '*256

class FileHandler(object):

    def __init__(self):
        pass

    def write_message_history(self):
        try:
            print 'Writing message history to file <' + history_path + '>...'
            history_file = codecs.open(history_path, 'w', 'utf-8', 'strict', buffer_size)
            pickle.dump(message_handler.get_message_history(), history_file)
            print 'Message history successfully saved.'
        except Exception, e:
            print 'ERROR: Unable to write message history.'
            print e

    def read_message_history(self):
        try:
            print 'Reading message history from file <' + history_path + '>...'
            history_file = open(history_path, 'rU', buffer_size)
            message_handler.set_message_history(pickle.load(history_file))
            message_handler.set_unused_message_id(len(message_handler.get_message_history()))
            print '...message history loaded into memory.'
        except Exception, e:
            print 'ERROR: Unable to read saved message history.'
            print e
            
    def write_user_credentials(self):
        try:
            print 'Writing user credentials to file <' + credentials_path + '>...'
            credentials_file = codecs.open(credentials_path, 'w', 'utf-8', 'strict', buffer_size)
            cred_keys = user_handler.credentials.keys()
            for each in cred_keys:
                print 'Saving credentials for user: ', each
                try:
                    user = communication_handler.pad_this(each)
                    password = communication_handler.pad_this(user_handler.credentials[each])
                    credentials_file.write(user)
                    credentials_file.write(password)
                except:
                    print 'ERROR: Unable to save credentials of user',each,'.'
            credentials_file.close()
            print '...user credentials saved.'
        except Exception, e:
            print 'ERROR: Unable to save credentials.'
            print e

    def read_user_credentials(self): #FIX THIS
        try:
            print 'Reading user credentials from file <' + credentials_path + '>...'
            credentials_file = codecs.open(credentials_path, 'rU', 'utf-8', 'strict', buffer_size)
            is_user = True
            is_password = False
            this_user = ''
            credentials_list = []
            for each in credentials_file:
                credentials_list = each.split()

            for each in credentials_list:
                if is_user == True:
                    is_user = False
                    is_password = True
                    this_user = each.strip()
                else:
                    is_user = True
                    is_password = False
                    user_handler.credentials[this_user] = each.strip()
                    this_user = ''
            print '...user credentials loaded into memory.'
        except Exception, e:
            print 'ERROR: User credentials unable to be loaded.'
            print e
            
                
class ClientHandler(object):
    clients = {}
    continue_listening = True
    def __init__(self):
        welcome_socket.bind((server_ip, server_welcome_port))
        welcome_socket.setblocking(1)
        print 'Server initialized.'
        
    def save_socket(self, info):
        global clients
        print 'Attempting to accept and finalize new connection...'
        print 'Socket:' + str(info[0])
        print 'Port:' + str(info[1])
        info[0].setblocking(1)
        info[0].settimeout(5)       # Prevents the program from staying indefinitely at a single client.
        user_id = user_handler.create_random_id()   # Give this user a random ID the server can identify him with.
        try:
            socket_thread = Thread(target=communication_handler.process_input, args=(info[0], user_id))
            self.add_client(user_id, info[0], info[1], socket_thread)
            socket_thread.start()
            message_handler.post_server_message(str(user_handler.identify_user(user_id)) + ' connected to server.', get_time())
            print 'Assigned user id of ' + str(user_id) + ' to socket ' + str(info[0]) + '.'
        except Exception, e:
            print 'ERROR: Unable to start thread for new client.'
            print e
            
    def get_client_with(self, user_id):
        try:
            return self.clients[user_id]
        except KeyError:
            print 'ERROR: Key failure.'
            return 0
    
    def get_clients(self):
        return self.clients

    def add_client(self, user_id, client_socket, client_port, client_thread):
        self.clients[user_id] = [client_socket, client_port, client_thread]
        
    def is_valid_socket(self, socket_to_check):
        try:
            message = socket_to_check.send('') # Send a message to test connection.
            return True
        except Exception, e:
            print e
            return False

    def listen_for_connections(self):
        print 'Server is now listening for connections.'
        welcome_socket.listen(timeout)
        while continue_listening:
            try:
                info = welcome_socket.accept()
                self.save_socket(info)
                print 'New connection finalized.'
            except Exception, e:
                print 'ERROR: Unable to accept new client.', e
        
    def validate_all_sockets(self):
        while continue_validating:
            invalid_sockets = []
            # Avoid errors related to changing size of collection while iterating.
            client_keys = self.clients.keys()

            for each in client_keys:
                try:
                    if self.is_valid_socket(self.clients[each][0])==False:
                        self.clients[each][0].close()
                        invalid_sockets.append(each)
                except Exception, e:
                    print 'ERROR: Validation fault, client ID:' + str(each) +'.'
                    print e
            self.remove_sockets(invalid_sockets)

    def remove_sockets(self, invalid_sockets):
        for each in invalid_sockets:
            try:
                del self.clients[each]
                print 'Client with ID', each, 'disconnected.'
                message_handler.post_server_message(str(user_handler.identify_user(each)) + ' disconnected.', get_time())
                user_handler.remove_user_with_id(each)
            except Exception, e:
                print 'ERROR: Unable to remove invalid socket of client' + str(each)
                print e


            
if __name__ == "__main__":
        main()
