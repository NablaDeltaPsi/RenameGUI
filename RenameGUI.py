import tkinter as tk
from tkinter import messagebox
import tkinter.font
import glob
import os
import shutil
import re
from ctypes import windll
import piexif
import datetime as dt

global version
version = '1.1'

def blanks(number):
    string = ""
    for i in range(number):
        string = string + " "
    return string

def two_digits(integer):
    if integer < 10:
        string = "0" + str(integer)
    else:
        string = str(integer)
    return string

def pts(*args):
    # accepts str, str+'p', int, float and returns sum as str+'p'
    # '-' sets the following argument negative
    # pts(0.5, '1.5', '-', '3p') = '-1p'
    number = 0
    factor = 1
    for i in range(len(args)):
        if args[i]=='-':
            factor = -1
        elif args[i] == '':
            factor = 1
            continue
        else:
            try:
                number = number + factor*float(args[i])
            except:
                if args[i][len(args[i])-1] == 'p':
                    try:
                        number = number + factor*float(args[i][0:len(args[i])-1])
                    except:
                        print("WARNING: Could not add value to points!")
                else:
                    print("WARNING: Could not add value to points!")
            factor = 1
    return str(number) + "p"

def getImageDateTakenAttribute(filename):
    try:
        exif_dict = piexif.load(filename)
        # DT  = exif_dict['0th'][piexif.ImageIFD.DateTime]
        DTO = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]
        # DTD = exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized]
    except:
        DTO = 'empty'
    return DTO

def renameWithUserCheck(old_files, new_files, backup, fontsize):

    # CONSISTENCY CHECK
    if not len(new_files) == len(old_files):
        print("\n" + ">> Interrupt: Something went wrong (code issue)!")
        return

    # LIST OF CHANGED FILES
    changing_files_from = []
    changing_files_to = []
    for i in range(len(old_files)):
        if not new_files[i] == old_files[i]:
            changing_files_from.append(old_files[i])
            changing_files_to.append(new_files[i])

    # GET MAXIMUM LENGTH FOR PRINTING
    max_length_from = 1
    max_length_to = 1
    for i in range(len(changing_files_from)):
        if len(os.path.basename(changing_files_from[i])) > max_length_from:
            max_length_from = len(os.path.basename(changing_files_from[i]))
        if len(os.path.basename(changing_files_to[i])) > max_length_to:
            max_length_to = len(os.path.basename(changing_files_to[i]))

    # USER CHECK
    print("\n" + blanks(3) + "User check" + "\n")
    message = "Do you want to rename these files?" + "\n\n"
    if not len(changing_files_from) == 0:
        message = message + "Path: " + os.path.dirname(changing_files_from[0]) + os.sep + "\n\n"
    for i in range(len(changing_files_from)):
        message = message + \
        os.path.basename(changing_files_from[i]).ljust(max_length_from) + "  >  " + \
        os.path.basename(changing_files_to[i]).ljust(max_length_to)   + "\n"
    msb = OwnMessagebox(fontsize, "Check files", message)
    if msb.choice==-1 or msb.choice==0:
        print("\n" + ">> Interrupted by user.")
        return

    # SKIP EMPTY HERE
    if len(changing_files_from) == 0:
        print("\n" + ">> Skip: Empty changing list.")
        return

    # BACKUP
    if backup and not len(changing_files_from) == 0:
        # first, find where to put the old files
        basic_path = os.path.dirname(changing_files_from[0]) + os.sep
        folders_found = 0
        while True:
            maybe_new_path = basic_path + "_old_files_" + str(folders_found + 1)
            if not os.path.exists(maybe_new_path):
                os.mkdir(maybe_new_path)
                new_path = maybe_new_path
                break
            else:
                folders_found = folders_found + 1
        print(blanks(3) + "Backup to: " + new_path + os.sep)
        # copy backup
        for i in range(len(changing_files_from)):
            shutil.copy2(basic_path + os.path.basename(changing_files_from[i]), new_path + os.sep + os.path.basename(changing_files_from[i]))
            print(blanks(3) + "COPY TO: " + new_path + os.sep + os.path.basename(changing_files_from[i]))

    # RENAME
    for i in range(len(changing_files_from)):
        if not os.path.isfile(changing_files_to[i]):
            print(blanks(3) + "OLD: " + changing_files_from[i])
            print(blanks(3) + "NEW: " + changing_files_to[i])
            os.rename(changing_files_from[i], changing_files_to[i])
        else:
            print(">> Skip: " + changing_files_to[i] + " already exists!")

class OwnMessagebox():

    def __init__(self, fontsize, title, msg):

        self.choice = -1
        self.root = tk.Toplevel()
        self.root.title(title)
        self.root.geometry("500x400+400+200")
        self.root.attributes("-topmost", True)

        self.fontsize = fontsize
        self.default_font = tk.font.nametofont("TkDefaultFont")
        self.text_font = tk.font.nametofont("TkTextFont")
        self.default_font.configure(size=self.fontsize)
        self.text_font.configure(size=self.fontsize)
        
        bottom_height = pts(60)
        edge = pts(10)
        button_height = pts(17)
        button_width = pts(60)
        button_distance = pts(5)
        scrollbar_width = pts(15)

        self.label_message = tk.Text(self.root, wrap="none")
        self.label_message.place(x=edge, y=edge, relwidth=1, width=pts('-', edge, '-', scrollbar_width), relheight=1, height=pts('-', bottom_height), anchor='nw')
        self.label_message.insert('end', msg)
        self.label_message.config(state='disabled')

        self.scrollbx = tk.Scrollbar(self.root, orient='horizontal', command=self.label_message.xview)
        self.scrollbx.place(x=edge, rely=1, y=pts(edge, '-', bottom_height), relwidth=1, width=pts('-', edge, '-', edge, '-', scrollbar_width), height=scrollbar_width, anchor='nw')
        self.label_message['xscrollcommand'] = self.scrollbx.set

        self.scrollby = tk.Scrollbar(self.root, orient='vertical', command=self.label_message.yview)
        self.scrollby.place(relx=1, x=pts('-', edge), y=edge, width=scrollbar_width, height=pts('-', bottom_height), relheight=1, anchor='ne')
        self.label_message['yscrollcommand'] = self.scrollby.set

        self.button_yes = tk.Button(self.root, text="Yes",command=self.chose_yes)
        self.button_yes.place(relx=0.5, x=pts('-', button_distance), rely=1, y=pts('-', edge), width=button_width, height=button_height, anchor='se')
        self.button_no = tk.Button(self.root, text="No",command=self.chose_no)
        self.button_no.place(relx=0.5, x=button_distance, rely=1, y=pts('-', edge), width=button_width, height=button_height, anchor='sw')

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.wait_window()

    def on_closing(self):
        self.root.destroy()
        
    def chose_yes(self):
        self.root.destroy()
        self.choice = 1

    def chose_no(self):
        self.root.destroy()
        self.choice = 0


class NewGUI():
    def __init__(self):
        
        global version
        
        self.root = tk.Tk()
        self.root.title("RenameGUI (v" + version + ")")
        self.root.attributes("-topmost", True)

        # reset saved window position
        if os.path.isfile("RenameGUI.conf"): 
            with open("RenameGUI.conf", "r") as conf: 
                lines = conf.readlines()
                self.root.geometry(lines[0].strip())
                linenr = 1
                configs = []
                while True:
                    try:
                        configs.append(lines[linenr].strip())
                    except:
                        break
                    linenr += 1
        else:
            self.root.geometry("400x120+400+200")
            configs =['File path', 'False', 'True', 'False']
        self.root.protocol("WM_DELETE_WINDOW",  self.on_close)

        try:
            self.root.iconbitmap('RenameGUI.ico')
            self.root.update() # important: recalculate the window dimensions
        except:
            print("Icon nicht gefunden... Fahre fort.")
        try:
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            print("SetProcessDpiAwareness(1) nicht erfolgreich... fahre fort.")

        # get fontsize
        self.fontsize = 10
        self.default_font = tk.font.nametofont("TkDefaultFont")
        self.text_font = tk.font.nametofont("TkTextFont")
        self.default_font.configure(size=self.fontsize)
        self.text_font.configure(size=self.fontsize)

        entry_height  = pts(self.fontsize * 1.6)
        button_height = pts(self.fontsize * 1.7)
        edge_distance = pts(self.fontsize * 0.6)

        # menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # start
        menubar.add_command(label="Start", command=self.rename_files)
        menubar.add_command(label="Switch", command=self.switch_strings)

        # options
        anzeige = tk.Menu(menubar, tearoff=0)
        self.check_backup = tk.BooleanVar()
        self.check_case = tk.BooleanVar()
        self.check_regex = tk.BooleanVar()
        self.check_backup.set(configs[1])
        self.check_case.set(configs[2])
        self.check_regex.set(configs[3])
        anzeige.add_checkbutton(label="Backup", onvalue=1, offvalue=0, variable=self.check_backup)
        anzeige.add_checkbutton(label="Case sensitive", onvalue=1, offvalue=0, variable=self.check_case)
        anzeige.add_checkbutton(label="Regex", onvalue=1, offvalue=0, variable=self.check_regex)
        menubar.add_cascade(label="Options", menu=anzeige)

        self.entry_path = tk.Entry(fg='grey')
        self.entry_path_default = configs[0]
        #self.entry_path_default = "D:\\Computer\\Python\\RenameGUI\\testfiles"        
        self.entry_path.insert(0, self.entry_path_default)
        self.entry_path.place(x=edge_distance, y=edge_distance, height=entry_height, relwidth=1, width=pts('-', edge_distance, '-', edge_distance), anchor='nw')
        self.entry_path.bind("<FocusIn>", self.focus_in_entry_path)
        
        self.entry_from = tk.Entry(fg='grey')
        self.entry_from_default = "Change from"
        #self.entry_from_default = "^"
        self.entry_from.insert(0, self.entry_from_default)
        self.entry_from.place(x=edge_distance, rely=0.5, height=entry_height, relwidth=0.5, width=pts('-', edge_distance, '-', edge_distance), anchor='w')
        self.entry_from.bind("<FocusIn>", self.focus_in_entry_from)
        
        self.entry_to = tk.Entry(fg='grey')
        self.entry_to_default = "Change to (\\1, <date/time_t/m/c>)"
        #self.entry_to_default = "<date_c>_<date_m>_<date_t>_"
        self.entry_to.insert(0, self.entry_to_default)
        self.entry_to.place(relx=1, x=pts('-', edge_distance), rely=0.5, height=entry_height, relwidth=0.5, width=pts('-', edge_distance, '-', edge_distance), anchor='e')
        self.entry_to.bind("<FocusIn>", self.focus_in_entry_to)

        self.root.bind_all("<1>", lambda event:event.widget.focus_set())
        self.root.mainloop()

    def switch_strings(self):
        entered_from = self.entry_from.get()
        entered_to = self.entry_to.get()
        self.entry_from.delete(0, "end")
        self.entry_to.delete(0, "end")
        self.entry_from.insert(0, entered_to)
        self.entry_to.insert(0, entered_from)

    def focus_in_entry_path(self, *args):
        if (self.entry_path.get() == self.entry_path_default):
            self.entry_path.delete(0, tk.END)
            self.entry_path.config(fg='black')

    def focus_in_entry_from(self, *args):
        if (self.entry_from.get() == self.entry_from_default):
            self.entry_from.delete(0, tk.END)
            self.entry_from.config(fg='black')

    def focus_in_entry_to(self, *args):
        if (self.entry_to.get() == self.entry_to_default):
            self.entry_to.delete(0, tk.END)
            self.entry_to.config(fg='black')

    def rename_files(self):

        # process entered strings
        entered_path = self.entry_path.get()
        entered_from = self.entry_from.get()
        entered_to = self.entry_to.get()

        if len(entered_path) == 0:
            print(">> Interrupted: Enter path!")
            return            

        if len(entered_from) == 0:
            print(">> Interrupted: Enter change_from!")
            return            

        if entered_path[len(entered_path) - 1] != os.sep:
            entered_path = entered_path + os.sep
            print(blanks(3) + entered_path)

        if not os.path.isdir(entered_path):
            print(">> Interrupted: Path not valid!")
            return

        # find all files in directory
        old_files = glob.glob(entered_path + "*.*", recursive=False)
        new_files = []

        for i in range(len(old_files)):
            print("\n" + blanks(3) + "FILE: " + old_files[i])
            old_files[i] = os.path.basename(old_files[i])  # only filenames

            # replace <date> and <time> for found attributes
            this_entered_to = entered_to
            if not ((entered_to.find("<date_t>")==-1) and (entered_to.find("<time_t>")==-1)):
                thisdate = str(getImageDateTakenAttribute(entered_path + os.sep + old_files[i]))
                print(blanks(3) + "date_t: " + thisdate)
                if thisdate == 'empty':
                    print(blanks(3) + "Skip: No date_t found!")
                    new_files.append(old_files[i])
                    continue
                else:
                    thisdate = thisdate[2:len(thisdate)-1]
                    y = thisdate[2:4]
                    m = thisdate[5:7]
                    d = thisdate[8:10]
                    h = thisdate[11:13]
                    mnt = thisdate[14:16]
                    sec = thisdate[17:19]
                    this_entered_to = re.sub("<date_t>", str(y) + str(m) + str(d), this_entered_to)
                    this_entered_to = re.sub("<time_t>", str(h) + str(mnt), this_entered_to)
                    
            if not ((entered_to.find("<date_m>")==-1) and (entered_to.find("<time_m>")==-1)):
                thisdate = dt.datetime.fromtimestamp(os.path.getmtime(entered_path + os.sep + old_files[i]))
                print(blanks(3) + "date_m: " + str(thisdate))
                y = thisdate.year-2000
                m = thisdate.month
                d = thisdate.day
                h = thisdate.hour
                mnt = thisdate.minute
                sec = thisdate.second
                this_entered_to = re.sub("<date_m>", two_digits(y) + two_digits(m) + two_digits(d), this_entered_to)
                this_entered_to = re.sub("<time_m>", two_digits(h) + two_digits(mnt), this_entered_to)
                
            if not ((entered_to.find("<date_c>")==-1) and (entered_to.find("<time_c>")==-1)):
                thisdate = dt.datetime.fromtimestamp(os.path.getctime(entered_path + os.sep + old_files[i]))
                print(blanks(3) + "date_c: " + str(thisdate))
                y = thisdate.year-2000
                m = thisdate.month
                d = thisdate.day
                h = thisdate.hour
                mnt = thisdate.minute
                sec = thisdate.second
                this_entered_to = re.sub("<date_c>", two_digits(y) + two_digits(m) + two_digits(d), this_entered_to)
                this_entered_to = re.sub("<time_c>", two_digits(h) + two_digits(mnt), this_entered_to)

            # case sensitive checkbox
            if self.check_case.get():
                this_flag = re.IGNORECASE
            else:
                this_flag = 0

            # regex checkbox: if no regex, escape all characters in entered_from
            if not self.check_regex.get():
                this_entered_from = re.escape(entered_from)
                print(blanks(3) + "Escape from " + entered_from + " to " + this_entered_from)
            else:
                this_entered_from = entered_from

            # Finally, replace
            new_files.append(re.sub(this_entered_from, this_entered_to, old_files[i], flags=this_flag))                        

            if new_files[i] == old_files[i]:
                print(blanks(3) + "No match")
            else:
                print(blanks(3) + "Found match")

        # COMPLETE FILENAMES
        changing_files_from = []
        changing_files_to = []
        for i in range(len(old_files)):
            if not new_files[i] == old_files[i]:
                changing_files_from.append(entered_path + old_files[i])
                changing_files_to.append(entered_path + new_files[i])

        # rename with static method
        renameWithUserCheck(changing_files_from, changing_files_to, self.check_backup.get(), self.fontsize)

        print("\n" + blanks(3) + "<<<<<<<<<<<< FINISHED >>>>>>>>>>>>")

    def on_close(self):
        with open("RenameGUI.conf", "w") as conf: 
            conf.write(self.root.geometry() + "\n")
            conf.write(self.entry_path.get() + "\n")
            conf.write(str(self.check_backup.get()) + "\n")
            conf.write(str(self.check_case.get()) + "\n")
            conf.write(str(self.check_regex.get()))
        self.root.destroy()

if __name__ == '__main__':
    new = NewGUI()

