import keyboard
import tkinter as tk
import time
from win32.win32gui import GetWindowText, GetForegroundWindow
import tkinter.filedialog as tkFileDialog
import os
import shutil
import traceback

arVersion = "v1.1.9"


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

        tk.Label(text="Minecraft Auto Resetter by DuncanRuns\n\nHow to use:\nLeave a world to automatically reset and generate another one.\nHold escape while leaving a world to prevent resetting.").grid(
            row=0, column=0, padx=5, pady=5)

        self.optionsFrame = tk.Frame(self)
        self.optionsFrame.grid(row=1, column=0)

        self.directFrame = tk.LabelFrame(self.optionsFrame)
        self.directFrame.grid(row=0, column=0, padx=5, pady=5, sticky="n")

        tk.Label(self.directFrame, text=".minecraft Directory:").grid(
            row=0, column=0, padx=5, pady=5)
        self.dirLabel = tk.Label(
            self.directFrame, text=self.path.replace(" ", " "), wraplength=100, justify="left")
        self.dirLabel.grid(row=1, column=0, padx=5, pady=5)
        tk.Button(self.directFrame, command=self.setPathButton,
                  text="Change Directory").grid(row=2, column=0, padx=5, pady=5)

        self.macroFrame = tk.LabelFrame(self.optionsFrame)
        self.macroFrame.grid(row=0, column=1, padx=5, pady=5, sticky="n")

        tk.Label(self.macroFrame, text="Current Macro:").grid(
            row=0, column=0, padx=5, pady=5)
        self.macroLabel = tk.Label(self.macroFrame, text=self.version)
        self.macroLabel.grid(row=1, column=0, padx=5, pady=5)

        self.macroButtonFrame = tk.Frame(self.macroFrame)
        self.macroButtonFrame.grid(row=2, column=0, padx=5, pady=5)

        tk.Button(self.macroButtonFrame, text="1.16",
                  command=self.set116, width=10).grid(row=0, column=0)
        tk.Button(self.macroButtonFrame, text="1.14/1.15",
                  command=self.set114, width=10).grid(row=1, column=0)
        tk.Button(self.macroButtonFrame, text="1.14/1.15 HC",
                  command=self.set114HC, width=10).grid(row=2, column=0)

        self.worldFrame = tk.LabelFrame(self.optionsFrame)
        self.worldFrame.grid(row=0, column=2, padx=5, pady=5)

        tk.Label(self.worldFrame, text="World Deletion:").grid(
            row=0, column=0, padx=5, pady=5)
        self.worldVar = tk.BooleanVar(self.worldFrame, self.worldDeletion)
        tk.Checkbutton(self.worldFrame, variable=self.worldVar).grid(
            row=1, column=0, padx=5, pady=5)
        self.safetyManager = None
        tk.Button(self.worldFrame, command=self.openSafetyManager,
                  text="Manage Safe\nWorlds").grid(row=2, column=0, padx=5, pady=5)

        self.oldPath = ""
        self.after(0, self.loop)

    def openSafetyManager(self, x=0):
        if self.safetyManager is None:
            self.safetyManager = SafetyManager(self)

    def loop(self):
        try:
            self.loopProcess()
        except:
            print("ERROR FOUND BELOW, PROBABLY TELL DUNCAN ABOUT THIS")
            traceback.print_exc()

        self.after(50, self.loop)

    def loopProcess(self):
        if self.worldDeletion != self.worldVar.get():
            self.worldDeletion = self.worldVar.get()
            self.save()

        if self.oldPath != self.path:
            self.logPath = os.path.join(self.path, "logs", "latest.log")
            self.logMTime = 0
            self.logLastLine = 0
            self.oldPath = self.path
            self.state = -1

        if os.path.isfile(self.logPath):

            newMTime = os.path.getmtime(self.logPath)
            if newMTime != self.logMTime:

                self.logMTime = newMTime

                if self.state != -1:
                    with open(self.logPath, "r") as logFile:
                        lines = logFile.readlines()
                        newLastLine = len(lines)
                        if newLastLine != self.logLastLine:
                            for line in lines[self.logLastLine:]:
                                print(line.rstrip(), "- State:", self.state)
                                if self.state == 0:
                                    if "Stopping singleplayer server as player logged out" in line:
                                        print("Waiting for world to save.")
                                        self.state = 1
                                        self.saveChecks = [False, False, False]
                                elif self.state == 1:
                                    if "Saving chunks for level" in line and "/minecraft:overworld" in line:
                                        self.saveChecks[0] = True
                                    elif "Saving chunks for level" in line and "/minecraft:the_nether" in line:
                                        self.saveChecks[1] = True
                                    elif "Saving chunks for level" in line and "/minecraft:the_end" in line:
                                        self.saveChecks[2] = True

                                    if self.saveChecks.count(True) == 3:
                                        self.state = 2
                                        self.chunkSaves = 0
                                elif self.state == 2:
                                    if "): All chunks are saved" in line and "ThreadedAnvilChunkStorage" in line:
                                        self.chunkSaves += 1
                                        if self.chunkSaves == 4:
                                            self.state = 3
                                            self.wfwttsTime = time.time()  # I'm not telling you what this stands for
                                elif self.state == 3:
                                    if "Stopping worker threads" in line:
                                        self.state = 0
                                        print(
                                            "World saved, running macro and waiting for world exit.")
                                        self.runMacro()
                                    elif abs(time.time() - self.wfwttsTime) > 0.3:
                                        self.state = 0
                                        print(
                                            "World saved, running macro and waiting for world exit.")
                                        self.runMacro()
                            self.logLastLine = newLastLine
                        logFile.close()

        if self.state == -1:
            self.state = 0

    def set116(self):
        self.version = "1.16"
        self.macroLabel.config(text=self.version)
        self.save()

    def deleteWorlds(self):
        savesPath = os.path.join(self.path, "saves")
        worlds = [i for i in os.listdir(savesPath) if (os.path.isfile(os.path.join(
            savesPath, i, "level.dat")) and not os.path.isfile(os.path.join(savesPath, i, "Reset Safe.txt")))]
        worlds.sort(reverse=True, key=lambda x: os.path.getmtime(
            os.path.join(savesPath, x)))
        if len(worlds) > 5:
            for world in worlds[5:]:
                shutil.rmtree(os.path.join(savesPath, world))

    def set114(self):
        self.version = "1.14/1.15"
        self.macroLabel.config(text=self.version)
        self.save()

    def set114HC(self):
        self.version = "1.14/1.15 HC"
        self.macroLabel.config(text=self.version)
        self.save()

    def setPathButton(self):
        x = tkFileDialog.askdirectory()
        if x is not None and x != "":
            self.setPath(x)

    def setPath(self, path):
        self.path = path.replace("\\", "/")
        if self.path.split("/")[-1] in ["logs", "saves"]:
            self.path = os.path.abspath(os.path.join(
                self.path, "..")).replace("\\", "/")
        try:
            self.dirLabel.config(text=self.path.replace(" ", " "))
            self.save()
        except:
            pass

    def optionsInit(self):
        self.oPath = os.path.expanduser(
            "~/AppData/Roaming/.automcreset").replace("\\", "/")

        if not os.path.isdir(self.oPath):
            os.mkdir(self.oPath)

        self.ofPath = os.path.join(self.oPath, "settings.txt")

        if not os.path.isfile(self.ofPath):
            with open(self.ofPath, "w+") as oFile:
                oFile.write(os.path.expanduser(
                    "~/AppData/Roaming/.minecraft").replace("\\", "/")+"\n"+"1.16")

        with open(self.ofPath, "r") as oFile:
            settings = [i.rstrip() for i in oFile.readlines()]
            self.setPath(settings[0])
            self.version = settings[1]
            if len(settings) < 3:
                self.worldDeletion = False
            else:
                self.worldDeletion = True if settings[2] == "World Deletion = On" else False

    def save(self):
        with open(self.ofPath, "w+") as oFile:
            oFile.write(self.path+"\n"+self.version+"\n" +
                        ("World Deletion = On" if self.worldVar.get() else "World Deletion = Off"))

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
                if keyboard.is_pressed("\x1b"):
                    print("Macro Canceled")
                    return
                if i == "t":
                    keyboard.press_and_release("\t")
                    time.sleep(0.05)
                elif i == "s":
                    keyboard.press_and_release(" ")
                    time.sleep(0.05)
                elif i == "e":
                    keyboard.press_and_release("\x1b")
                elif i == "w":
                    time.sleep(0.1)
        if self.worldDeletion:
            self.deleteWorlds()


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


class SafetyManager(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent

        self.title("World Safety Manager")
        self.protocol("WM_DELETE_WINDOW", self.exit)

        self.resizable(0, 0)

        self.worldFrame = tk.Frame(self)
        self.worldFrame.grid(row=0, column=0, padx=5, pady=5)

        tk.Label(self.worldFrame, text="World Name:").grid(row=0, column=0)
        self.entry = tk.Entry(self.worldFrame, width=30)
        self.entry.grid(row=0, column=1)
        tk.Button(self.worldFrame, text="AutoFill",
                  command=self.autocomplete).grid(row=0, column=2)

        self.buttonFrame = tk.Frame(self)
        self.buttonFrame.grid(row=1, column=0)

        tk.Button(self.buttonFrame, command=self.add,
                  text="Add Safety").grid(row=0, column=0, padx=5)
        tk.Button(self.buttonFrame, command=self.remove,
                  text="Remove Safety").grid(row=0, column=1, padx=5)

        self.response = tk.Label(self)
        self.response.grid(row=2, column=0, padx=5, pady=5)

    def autocomplete(self):
        words = [i.lower() for i in self.entry.get().rstrip().split()]
        for world in os.listdir(os.path.join(self.parent.path, "saves")):
            success = True
            for word in words:
                if word not in world.lower():
                    success = False
                    break
            if success:
                self.entry.delete(0, 'end')
                self.entry.insert(0, world)
                break

    def getEnter(self):
        entry = self.entry.get().rstrip()
        if entry == "":
            return False
        return os.path.join(self.parent.path, "saves", entry)

    def add(self, x=0):
        enter = self.getEnter()
        if not (enter == False) and os.path.isdir(enter):
            path = os.path.join(enter, "Reset Safe.txt")
            if os.path.isfile(path):
                self.respond("Error: World already has safety.")
            else:
                with open(path, "w+") as safetyFile:
                    safetyFile.write(
                        "This is a file created by Duncan's Auto Reset Macro.\nThis file marks a world so that the auto world deletion does not delete it.")
                    safetyFile.close()
                self.respond("Added safety to world.")
        else:
            self.respond("Error: World not found")

    def remove(self, x=0):
        enter = self.getEnter()
        if not (enter == False) and os.path.isdir(enter):
            path = os.path.join(self.getEnter(), "Reset Safe.txt")
            if os.path.isfile(path):
                os.remove(path)
                self.respond("Removed safety from world.")
            else:
                self.respond("Error: World had no safety.")
        else:
            self.respond("Error: World not found")

    def respond(self, message):
        self.response.config(text=str(message))

    def exit(self):
        self.parent.safetyManager = None
        self.destroy()


if __name__ == "__main__":
    ara = AutoResetApp()
    ara.mainloop()
