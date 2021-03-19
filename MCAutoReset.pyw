import keyboard
import tkinter as tk
import time
from win32.win32gui import GetWindowText, GetForegroundWindow
from Trackers import LogsTracker
import tkinter.filedialog as tkFileDialog
import os

arVersion = "v1.0.3"


def resource_path(relative_path):
    try:
        from sys import _MEIPASS
        base_path = _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class AutoResetApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Minecraft Auto Resetter "+arVersion)
        self.resizable(0, 0)

        self.iconbitmap(resource_path("Logo.ico"))

        self.optionsInit()
        self.logsTracker = None
        self.refreshLT()

        tk.Label(text="Minecraft Auto Resetter by DuncanRuns\n\nHow to use:\nLeave a world to automatically reset and generate another one.\nHold escape while leaving a world to prevent resetting.").grid(
            row=0, column=0, padx=5, pady=5)

        self.optionsFrame = tk.Frame(self)
        self.optionsFrame.grid(row=1, column=0)

        self.directFrame = tk.LabelFrame(self.optionsFrame)
        self.directFrame.grid(row=0, column=0, padx=5, pady=5)

        tk.Label(self.directFrame, text="Current Directory:").grid(
            row=0, column=0, padx=5, pady=5)
        self.dirLabel = tk.Label(
            self.directFrame, text=self.path.replace(" ", " "), wraplength=100, justify="left")
        self.dirLabel.grid(row=1, column=0, padx=5, pady=5)
        tk.Button(self.directFrame, command=self.setPath,
                  text="Change Directory").grid(row=2, column=0, padx=5, pady=5)

        self.macroFrame = tk.LabelFrame(self.optionsFrame)
        self.macroFrame.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.macroFrame, text="Current Macro:").grid(
            row=0, column=0, padx=5, pady=5)
        self.macroLabel = tk.Label(self.macroFrame, text=self.version)
        self.macroLabel.grid(row=1, column=0, padx=5, pady=5)

        self.macroButtonFrame = tk.Frame(self.macroFrame)
        self.macroButtonFrame.grid(row=2, column=0, padx=5, pady=5)

        tk.Button(self.macroButtonFrame,text="1.16",command=self.set116,width=10).grid(row=0,column=0)
        tk.Button(self.macroButtonFrame,text="1.14/1.15",command=self.set114,width=10).grid(row=1,column=0)
        tk.Button(self.macroButtonFrame,text="1.14/1.15 HC",command=self.set114HC,width=10).grid(row=2,column=0)

    def set116(self):
        self.version = "1.16"
        self.macroLabel.config(text=self.version)
        self.save()

    def set114(self):
        self.version = "1.14/1.15"
        self.macroLabel.config(text=self.version)
        self.save()

    def set114HC(self):
        self.version = "1.14/1.15 HC"
        self.macroLabel.config(text=self.version)
        self.save()

    def setPath(self):
        x = tkFileDialog.askdirectory()

        if x is not None and x != "":
            self.path = x.replace("\\", "/")
            if self.path.split("/")[-1] != "logs":
                self.path = os.path.join(self.path, "logs").replace("\\", "/")
            self.dirLabel.config(text=self.path.replace(" ", " "))
            self.save()
            self.refreshLT()

    def optionsInit(self):
        self.oPath = os.path.expanduser(
            "~/AppData/Roaming/.automcreset").replace("\\", "/")

        if not os.path.isdir(self.oPath):
            os.mkdir(self.oPath)

        self.ofPath = os.path.join(self.oPath, "settings.txt")

        if not os.path.isfile(self.ofPath):
            with open(self.ofPath, "w+") as oFile:
                oFile.write(os.path.expanduser(
                    "~/AppData/Roaming/.minecraft/logs").replace("\\", "/")+"\n"+"1.16")

        with open(self.ofPath, "r") as oFile:
            settings = [i.rstrip() for i in oFile.readlines()]
            self.path = settings[0]
            self.version = settings[1]

    def startListening(self):
        self.logsTracker.cancel()
        self.logsTracker.listenUntilExit(-1,self.waitForMenu)
    
    def waitForMenu(self):
        self.logsTracker.cancel()
        self.logsTracker.listenUntilMainMenu(-1,self.menuLoad)

    def refreshLT(self):
        if self.logsTracker is not None:
            self.logsTracker.cancel()
        self.logsTracker = LogsTracker(self.path)
        self.startListening()

    def menuLoad(self):
        while not WindowChecker.checkMainMenu() and not keyboard.is_pressed("esc"):
            time.sleep(0.1)
        if (not keyboard.is_pressed("esc")) and (not WindowChecker.checkInGame()):
            self.runMacro()
        self.startListening()

    def save(self):
        with open(self.ofPath, "w+") as oFile:
            oFile.write(self.path+"\n"+self.version)

    def runMacro(self):
        time.sleep(0.1)
        if WindowChecker.checkMainMenu():
            steps = ""
            if self.version == "1.16":
                steps = "etswtttsttsssttttts"
            elif self.version == "1.14/1.15":
                steps = "etswttttstttts"
            elif self.version == "1.14/1.15 HC":
                steps = "etswttttsttstts"
            for i in steps:
                if i == "t":
                    keyboard.press_and_release("tab")
                    time.sleep(0.05)
                elif i == "s":
                    keyboard.press_and_release("space")
                    time.sleep(0.05)
                elif i == "e":
                    keyboard.press_and_release("esc")
                elif i == "w":
                    time.sleep(0.1)


class WindowChecker:
    @staticmethod
    def checkMinecraft():
        window = GetWindowText(GetForegroundWindow()).lower()
        value = True
        for i in ["minecraft", "1."]:
            if i not in window:
                value = False
                break
        return value

    @staticmethod
    def checkMainMenu():
        value = WindowChecker.checkMinecraft()
        if value:
            window = GetWindowText(GetForegroundWindow()).lower()
            for i in ["multiplayer", "singleplayer", "realm"]:
                if i in window:
                    value = False
                    break
        return value

    @staticmethod
    def checkInGame():
        value = not WindowChecker.checkMinecraft()
        if not value:
            window = GetWindowText(GetForegroundWindow()).lower()
            for i in ["multiplayer", "singleplayer", "realm"]:
                if i in window:
                    value = True
                    break
        return value


if __name__ == "__main__":
    ara = AutoResetApp()
    ara.mainloop()
    ara.logsTracker.cancel()
