import threading
import os
import time

class LogsTracker:
    def __init__(self, path):
        self.path = path
        self.logPath = os.path.join(os.path.join(self.path, "latest.log"))
        self.running = True
        self.hasThread = False

    def cancel(self):
        self.running = False

    stop = cancel

    def refresh(self):
        self.start = time.time()

    def listenUntilWorldStart(self, timeout, responseCall, args=""):
        if not self.hasThread:
            threading.Thread(target=self._listenUWSThread,
                             args=(timeout, responseCall, args)).start()
        else:
            self.refresh()

    def _listenUWSThread(self, timeout, responseCall, args):
        self.hasThread = True
        try:
            if os.path.isfile(self.logPath):
                self.start = time.time()
                self.running = True
                lineLen = len(self.getLines())
                mtime = os.path.getmtime(self.logPath)
                while self.running and time.time() - self.start < timeout:
                    time.sleep(0.1)
                    newmtime = os.path.getmtime(self.logPath)
                    if mtime != newmtime:
                        mtime - newmtime
                        lines = self.getLines()
                        newLen = len(lines)
                        if newLen > lineLen:
                            for line in lines[lineLen: newLen]:
                                if "logged in with entity id" in line.lower():
                                    responseCall(*args)
                        lineLen = newLen
            else:
                print("latest.log not found")
        except ValueError:
            print(ValueError)
        self.hasThread = False
        self.running = False

    def listenUntilMainMenu(self, timeout, responseCall, args=""):
        if not self.hasThread:
            threading.Thread(target=self._listenUMMThread,
                             args=(timeout, responseCall, args)).start()
        else:
            self.refresh()

    def _listenUMMThread(self, timeout, responseCall, args):
        self.hasThread = True
        try:
            if os.path.isfile(self.logPath):
                self.start = time.time()
                self.running = True
                lineLen = len(self.getLines())
                mtime = os.path.getmtime(self.logPath)
                while self.running and (timeout == -1 or time.time() - self.start < timeout):
                    time.sleep(0.1)
                    newmtime = os.path.getmtime(self.logPath)
                    if mtime != newmtime:
                        mtime - newmtime
                        lines = self.getLines()
                        newLen = len(lines)
                        if newLen > lineLen:
                            for line in lines[lineLen: newLen]:
                                if "stopping worker threads" in line.lower():
                                    responseCall(*args)
                        lineLen = newLen
            else:
                print("latest.log not found")
        except ValueError:
            print(ValueError)
        self.hasThread = False
        self.running = False

    def getLines(self):
        with open(self.logPath) as logFile:
            lines = [i.rstrip() for i in logFile.readlines()]
            logFile.close()
            return lines