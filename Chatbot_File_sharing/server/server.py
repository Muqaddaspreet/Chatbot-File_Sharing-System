import socket
import random
from threading import Thread
import os
import shutil
from pathlib import Path
import time
import string


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None

    def start(self):
        """
        1) Create server, bind and start listening.
        2) Accept client connections and serve the requested commands.

        Note: Use ClientThread for each client connection.
        """
        # Create a socket

        # Bind the socket to the specified address and port

        # Listen for incoming connections

        # print(f"Server listening on {self.host}:{self.port}")

        # while True:
        # Accept incoming connections
        # print(f"Accepted connection from {client_address}")
        # send random eof token

        # try:
        #     # Handle the client requests using ClientThread
        # except Exception as e:
        #     print(f"Error: {e}")
        # finally:
        #     print("Connection closed.")
        #     client_socket.close()

        # raise NotImplementedError("Your implementation here.")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host} : {self.port}")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Accepted connection from {client_address}")
            # client_socket.sendall(self.generate_random_eof_token().encode())
            clientThread = ClientThread(self, client_socket, client_address, self.generate_random_eof_token())
            clientThread.start()
            #print("Connection closed.")
            #client_socket.close()

    def get_working_directory_info(self, working_directory):
        """
        Creates a string representation of a working directory and its contents.
        :param working_directory: path to the directory
        :return: string of the directory and its contents.
        """
        dirs = "\n-- " + "\n-- ".join(
            [i.name for i in Path(working_directory).iterdir() if i.is_dir()]
        )
        files = "\n-- " + "\n-- ".join(
            [i.name for i in Path(working_directory).iterdir() if i.is_file()]
        )
        dir_info = f"Current Directory: {working_directory}:\n|{dirs}{files}"
        return dir_info

    def generate_random_eof_token(self):
        """Helper method to generates a random token that starts with '<' and ends with '>'.
        The total length of the token (including '<' and '>') should be 10.
        Examples: '<1f56xc5d>', '<KfOVnVMV>'
        return: the generated token.
        """
        # raise NotImplementedError("Your implementation here.")
        random_token = '<' + (
            ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=8))) + '>'
        return random_token

    def receive_message_ending_with_token(self, active_socket, buffer_size, eof_token):
        """
        Same implementation as in receive_message_ending_with_token() in client.py
        A helper method to receives a bytearray message of arbitrary size sent on the socket.
        This method returns the message WITHOUT the eof_token at the end of the last packet.
        :param active_socket: a socket object that is connected to the server
        :param buffer_size: the buffer size of each recv() call
        :param eof_token: a token that denotes the end of the message.
        :return: a bytearray message with the eof_token stripped from the end.
        """
        # raise NotImplementedError("Your implementation here.")
        data = bytearray()
        while True:
            packet = active_socket.recv(buffer_size)
            data += packet
            if packet[-10:] == eof_token.encode():
                data = data[:-10]
                break
        return data

    def handle_cd(self, current_working_directory, new_working_directory):
        """
        Handles the client cd commands. Reads the client command and changes the current_working_directory variable
        accordingly. Returns the absolute path of the new current working directory.
        :param current_working_directory: string of current working directory
        :param new_working_directory: name of the sub directory or '..' for parent
        :return: absolute path of new current working directory
        """
        # raise NotImplementedError("Your implementation here.")
        # if current_working_directory.__contains__(new_working_directory) and current_working_directory != new_working_directory:
        #     new_working_directory = '..'
        path = os.path.join(current_working_directory, new_working_directory)
        os.chdir(path)
        new_current_working_directory = os.getcwd()
        return new_current_working_directory

    def handle_mkdir(self, current_working_directory, directory_name):
        """
        Handles the client mkdir commands. Creates a new sub directory with the given name in the current working directory.
        :param current_working_directory: string of current working directory
        :param directory_name: name of new sub directory
        """
        # raise NotImplementedError("Your implementation here.")
        path = os.path.join(current_working_directory, directory_name)
        os.mkdir(path)
        print(f"{directory_name} Directory Created Successfully")
        return current_working_directory

    def handle_rm(self, current_working_directory, object_name):
        """
        Handles the client rm commands. Removes the given file or sub directory. Uses the appropriate removal method
        based on the object type (directory/file).
        :param current_working_directory: string of current working directory
        :param object_name: name of sub directory or file to remove
        """
        # raise NotImplementedError("Your implementation here.")
        os.chdir(current_working_directory)
        if os.path.isdir(object_name):
            os.rmdir(object_name)
        if os.path.isfile(object_name):
            os.remove(object_name)
        print(f"{object_name} File or Directory Removed Successfully")

    def handle_ul(self, current_working_directory, file_name, service_socket, eof_token):
        """
        Handles the client ul commands. First, it reads the payload, i.e. file content from the client, then creates the
        file in the current working directory.
        Use the helper method: receive_message_ending_with_token() to receive the message from the client.
        :param current_working_directory: string of current working directory
        :param file_name: name of the file to be created.
        :param service_socket: active socket with the client to read the payload/contents from.
        :param eof_token: a token to indicate the end of the message.
        """
        # raise NotImplementedError("Your implementation here.")
        new_path = os.path.join(current_working_directory, file_name)
        f = open(new_path, 'wb')
        content_of_file = self.receive_message_ending_with_token(service_socket, 1024, eof_token)
        f.write(content_of_file)
        print(f"File {file_name} created at server")

    def handle_dl(self, current_working_directory, file_name, service_socket, eof_token):
        """
        Handles the client dl commands. First, it loads the given file as binary, then sends it to the client via the
        given socket.
        :param current_working_directory: string of current working directory
        :param file_name: name of the file to be sent to client
        :param service_socket: active service socket with the client
        :param eof_token: a token to indicate the end of the message.
        """
        # raise NotImplementedError("Your implementation here.")
        new_path = os.path.join(current_working_directory, file_name)
        f = open(new_path, 'rb')
        content_of_file = f.read()
        service_socket.sendall(content_of_file + eof_token.encode())
        print(f'Sent the contents of "{file_name}" to client')

    def handle_info(self, current_working_directory, file_name, service_socket, eof_token):
        """
        Handles the client info commands. Reads the size of a given file. 
        :param current_working_directory: string of current working directory
        :param file_name: name of sub directory or file to remove
        :param service_socket: active service socket with the client
        :param eof_token: a token to indicate the end of the message.
        """
        # raise NotImplementedError('Your implementation here.')

        new_path = os.path.join(current_working_directory, file_name)
        size_of_file = str(os.path.getsize(new_path))
        service_socket.sendall(size_of_file.encode() + eof_token.encode())
        print(f'Sent the size of "{file_name}" to client')

    def handle_mv(self, current_working_directory, file_name, destination_name):
        """
        Handles the client mv commands. First, it looks for the file in the current directory, then it moves or renames 
        to the destination file depending on the nature of the request.
        :param current_working_directory: string of current working directory
        :param file_name: name of the file tp be moved / renamed
        :param destination_name: destination directory or new filename
        """
        # raise NotImplementedError('Your implementation here.')
        src_path = os.path.join(current_working_directory, file_name)
        dst_path = os.path.join(destination_name, file_name)
        new_dst_path = os.path.join(current_working_directory, destination_name)
        if os.path.isdir(destination_name):
            shutil.move(src_path, dst_path)
        else:
            os.rename(src_path, new_dst_path)
        print(f'"{file_name}" moved or renamed successfully')


class ClientThread(Thread):
    def __init__(self, server: Server, service_socket: socket.socket, address: str, eof_token: str):
        Thread.__init__(self)
        self.server_obj = server
        self.service_socket = service_socket
        self.address = address
        self.eof_token = eof_token
        self.cwd = ""

    def run(self):
        # print ("Connection from : ", self.address)
        # raise NotImplementedError("Your implementation here.")
        #Thread.run(self)
        print(f"Connection from {self.address}")
        self.eof_token = self.server_obj.generate_random_eof_token()
        self.service_socket.sendall(self.eof_token.encode())
        print(f'Random_EOF_Token {self.eof_token} has been sent to {self.address}')
        self.cwd = os.getcwd()
        working_directory_str = ''.join(str(self.server_obj.get_working_directory_info(self.cwd) + str(self.eof_token)))
        self.service_socket.sendall(working_directory_str.encode())
        while True:
            cmd = self.server_obj.receive_message_ending_with_token(self.service_socket, 1024, self.eof_token)
            cmd = cmd.decode()
            if cmd.startswith("cd"):
                x = cmd[3:].split(" ")
                new_working_directory = x[0]
                self.cwd = self.server_obj.handle_cd(self.cwd, new_working_directory)
                print(f"The Directory has been changed and now the current directory is : {self.cwd}")
                # self.service_socket.sendall((self.cwd + self.eof_token).encode())

            elif cmd.startswith("mkdir"):
                x = cmd[6:].split(" ")
                new_working_directory = x[0]
                self.cwd = self.server_obj.handle_mkdir(self.cwd, new_working_directory)
                print(f"The Directory has been created and now the current directory is : {self.cwd}")
                # self.service_socket.sendall((self.cwd + self.eof_token).encode())

            elif cmd.startswith("rm"):
                x = cmd[3:].split(" ")
                filename = x[0]
                self.server_obj.handle_rm(self.cwd, filename)
                print(f"The file has been removed successfully")
                # self.service_socket.sendall((self.cwd + self.eof_token).encode())

            elif cmd.startswith("ul"):
                x = cmd[3:].split(" ")
                filename = x[0]
                self.server_obj.handle_ul(self.cwd, filename, self.service_socket, self.eof_token)
                print(f"The file {filename} has been uploaded successfully")
                # self.service_socket.sendall((self.cwd + self.eof_token).encode())

            elif cmd.startswith("dl"):
                x = cmd[3:].split(" ")
                filename = x[0]
                self.server_obj.handle_dl(self.cwd, filename, self.service_socket, self.eof_token)
                print(f"The file {filename} has been downloaded successfully")
                # self.service_socket.sendall((self.cwd + self.eof_token).encode())

            elif cmd.startswith("info"):
                x = cmd[5:].split(" ")
                filename = x[0]
                self.server_obj.handle_info(self.cwd, filename, self.service_socket, self.eof_token)
                print(f"The size {filename} of the file has been sent successfully")
                # self.service_socket.sendall((self.cwd + self.eof_token).encode())

            elif cmd.startswith("mv"):
                x = cmd[3:].split(" ")
                filename = x[0]
                destination_name = x[1]
                self.server_obj.handle_mv(self.cwd, filename, destination_name)
                print(f"The {filename} has been moved or downloaded successfully")
                # self.service_socket.sendall((self.cwd + self.eof_token).encode())

            elif cmd == 'exit':
                break

            time.sleep(1)
            self.service_socket.sendall((self.cwd + self.eof_token).encode())
        #print('Connection closed from:', self.address)

        # establish working directory

        # send the current dir info

        # while True:
        # get the command and arguments and call the corresponding method

        # sleep for 1 second

        # send current dir info

        # print('Connection closed from:', self.address)


def run_server():
    HOST = "127.0.0.1"
    PORT = 65438

    server = Server(HOST, PORT)
    server.start()


if __name__ == "__main__":
    run_server()
