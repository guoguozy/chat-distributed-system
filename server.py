from concurrent import futures

import grpc
import time
import tkinter
import tkinter.messagebox

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc

chater = 100

# inheriting here from the protobuf rpc file which is generated


class ChatServer(rpc.ChatServerServicer):

    def __init__(self):
        # List with all the chat history
        self.chats = []

    # The stream which will be used to send new messages to clients
    def ChatStream(self, request_iterator, context):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages

        :param request_iterator:
        :param context:
        :return:
        """
        lastindex = 0
        # For every client a infinite loop starts (in gRPC's own managed thread)
        while True:
            # Check if there are any new messages
            while len(self.chats) > lastindex:
                n = self.chats[lastindex]
                lastindex += 1
                yield n

    def SendNote(self, request: chat.Note, context):
        """
        This method is called when a clients sends a Note to the server.

        :param request:
        :param context:
        :return:
        """
        # this is only for the server console
        print("[{}] {}".format(request.name, request.message))
        # Add it to the chat history
        self.chats.append(request)
        # something needs to be returned required by protobuf language, we just return empty msg
        return chat.Empty()


def one_to_one():
    global chater
    chater = 3
    A.configure(state='disabled')
    tkinter.messagebox.showinfo('Tips','请勿开启超过2个客户端！\n否则将视为聊天被窥窃，程序保护性崩溃！\n')
    top.destroy()


def one_to_all():
    global chater
    chater = 10
    B.configure(state='disabled')
    tkinter.messagebox.showinfo('Tips','请勿开启超过10个客户端！\n否则将视为聊天被窥窃，终止程序！\n')
    top.destroy()


def openserver(chater):
    port = 11912  # a random port for the server to run on
    # the workers is like the amount of threads that can be opened at the same time, when there are 10 clients connected
    # then no more clients able to connect to the server.

    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=chater))  # create a gRPC server
    rpc.add_ChatServerServicer_to_server(
        ChatServer(), server)  # register the server to gRPC
    # gRPC basically manages all the threading and server responding logic, which is perfect!
    print('Starting server. Listening...')
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    # Server starts in background (in another thread) so keep waiting
    # if we don't wait here the main thread will end, which will end all the child threads, and thus the threads
    # from the server won't continue to work and stop the server
    while True:
        time.sleep(64 * 64 * 100)


if __name__ == '__main__':
    top = tkinter.Tk()
    top.title('SERVER')
    top.geometry('500x300')

    text = tkinter.Label(top, text='欢迎来到GZY实时聊天系统！')
    A = tkinter.Button(top, text="一对一聊天", command=one_to_one)
    B = tkinter.Button(top, text="一对多群聊", command=one_to_all)
    text.pack(expand='yes')
    A.pack(expand='yes')
    B.pack(expand='yes')

    top.mainloop()
    openserver(chater)
