
from ipykernel.kernelbase import Kernel
from subprocess import Popen, PIPE
import time
import sys
from threading  import Thread
from queue import Queue, Empty

stdout = sys.stdout

class IJava(Kernel):
    implementation = 'Java'
    implementation_version = '1.0'
    language = 'java' # syntax highlighting
    language_version = '21'
    language_info = {'name': 'java',
                     'mimetype': 'text/plain',
                     'extension': '.java'}
    banner = "Ijava"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.q = Queue()
        self.p = Popen(['jshell'], stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
        self._t = Thread(target=self.enqueue_output, args=(self.p.stdout, self.q))
        self._t.daemon = True # thread dies with the program
        self._t.start()
        
        time.sleep(0.5)
        self.get_welcome_msg()

        # self.send_receive_msg(['System.out.println(10); \n'])
        # self.send_receive_msg([
        #     'record Test(int val) { } \n',
        #     'var t = new Test(10) \n'
        #     'System.out.println(t) \n'
        # ])

    @staticmethod
    def enqueue_output(out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def get_welcome_msg(self):
        for i in range(10):
            try:
                msg = self.q.get_nowait().strip()
                print(f'[jshell] {msg}', file=stdout)
            except Empty:
                break

    @staticmethod
    def validate_message(msg):
        for b_open, b_close in [
            ('{', '}'),
            ('(', ')'),
            ('[', ']')
        ]:
            if msg.count(b_open) != msg.count(b_close):
                return (False, [f'Mismatched {b_open}/{b_close} pairs.'])

        return (True, None)

    def send_receive_msg(self, msg):
        msg_valid, errors = self.validate_message(msg)
        if not msg_valid:
            return errors

        self.p.stdin.writelines(msg + ';\n')
        self.p.stdin.flush()

        # timeout = 5 seconds
        time_start = time.time()
        output = []

        while True:
            try:
                output.append(self.q.get(timeout=0.1).strip())
                break
            except Empty:
                if (time.time() - time_start) > 5:
                    print('[error-timeout]', file=stdout)
                    return ['error-timeout']
        
        while True:
            try:
                output.append(self.q.get(timeout=0.1).strip())
            except Empty:
                break

        # test print
        # for line in output:
        #     print(f'[jshell] {line}', file=stdout)
        return output

    def do_execute(self, code, silent,
            store_history=True,
            user_expressions=None,
            allow_stdin=False
        ):

        out = self.send_receive_msg(code)
        print(code, file=stdout)
        print(out, file=stdout)

        if not silent:
            print('sending', file=stdout)

            self.send_response(self.iopub_socket, 'stream', {
                'name': 'stdout',
                'text': '\n'.join(out)
            })

        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }
    

