import tkinter as tk
from tkinter import ttk
from backend import Box
import platform
import tkintermapview


box = Box() # getting the box from backend

def use_port():
    if text_box_port.get():
        port = text_box_port.get()      
        id_and_status = box.connect(port)


def find_me():
    if find_me.sound_on:
        find_me.sound_on = False

        box.stopFindMe()
    else:
        find_me.sound_on = True
        box.findMe()

find_me.sound_on = False

def new_pos():
    new_pos.i+=1
new_pos.i = 0

title_color = "black"
main_bg_color = "cornsilk3"
main_text_color = "gray20"
results_bg_color = "gray20"
warning_text_color = "orange"
error_text_color = "brown1"
text_font = ("Arial",25)

window = tk.Tk()
window.geometry("1700x1000")
window.title("Forget-Me-Not Bridge")
window.configure(background=main_bg_color)
window.resizable(True, True)
window.minsize(width=1600, height=720)

if platform.system() == 'Windows':
    img = tk.PhotoImage(file='logo.png')
    window.iconphoto(False, img)

style = ttk.Style()
if platform.system() == 'Windows':
    style.configure('TNotebook.Tab', font=('URW Gothic L','15','bold'), padding=[10, 10])
else:
    style.configure('TNotebook.Tab', font=('Arial','15','bold'), padding=[10, 10])
style.configure('TButton', font=('Arial', '20', 'bold'))

notebook = ttk.Notebook(window)
notebook.pack(fill="both",expand=True)
frame1 = tk.Frame(notebook, width=1700, height=1000, bg=main_bg_color)
frame2 = tk.Frame(notebook, width=1700, height=1000, bg=main_bg_color)
frame3 = tk.Frame(notebook, width=1700, height=1000, bg=main_bg_color)

frame1.columnconfigure(0, weight=1)
frame2.columnconfigure(0, weight=1)
frame3.columnconfigure(0, weight=1)

notebook.add(frame1, text='Home')
notebook.add(frame2, text='Tools')
notebook.add(frame3, text='Location')


# TAB1

if platform.system() == 'Windows':
    title_label = tk.Label(frame1, text="Forget-Me-Not", font=("Arial", 75, "bold"),
                       bg=main_bg_color, fg=title_color, justify="center", pady=50)
else:
    title_label = tk.Label(frame1, text="Forget-Me-Not", font=("Arial", 75, "bold"),
                       bg=main_bg_color, fg=title_color, justify="center", pady=50)
title_label.grid(row=0, sticky = "ew")

# CONNECTION FRAME
connection_frame = tk.Frame(frame1, width=1700, height=200, pady=25, bg=main_bg_color)
connection_frame.grid(row=1, column=0, sticky='w', padx=100)

box_label = tk.Label(connection_frame, text="Box connected:",font=text_font, bg=main_bg_color)
box_label.grid(row=0, column=0)

box_label_led_red = tk.Label(connection_frame, text="Out",bg="red",font=text_font, padx=25)
box_label_led_red.grid(row=0,column=1, padx=25)

disconnect_button = ttk.Button(connection_frame, text="Disconnect", command=box.disconnect)
disconnect_button.grid(row=0, column=2)

#INSERT PORT FRAME
insert_port_frame = tk.Frame(frame1, width=1700, height=200, pady=25, bg=main_bg_color)
insert_port_frame.grid(row=2, column=0, sticky='w', padx=100)

label_insert_port = tk.Label(insert_port_frame, text="Porta di connessione:",font=text_font, bg=main_bg_color)
label_insert_port.grid(row=0, column=0, sticky='we')

text_box_port = tk.Entry(insert_port_frame, font=text_font)
text_box_port.grid(row=0, column=1, sticky="we", pady=25, padx=25)

ok_button = ttk.Button(insert_port_frame, text="OK", command=use_port)
ok_button.grid(row=0, column=2)


# RETRIVE AND SHOW ERROR LIST
errors_frame = tk.Frame(frame1, bg=results_bg_color, bd=0)  # frame containing error received
errors_frame.grid(row=3, sticky="NEWS", padx=50, pady=50)


# TAB2

if platform.system() == 'Windows':
    title2_label = tk.Label(frame2, text="Tools List", font=("Arial", 50, "bold"),
                       bg=main_bg_color, fg=title_color, justify="center", pady=50, padx=50)
else:
    title2_label = tk.Label(frame2, text="Tools List", font=("Arial", 50, "bold"),
                       bg=main_bg_color, fg=title_color, justify="center", pady=50, padx=50)
title2_label.grid(row=0, sticky = "w")

# RETRIVE AND SHOW TOOLS LIST
tools_frame = tk.Frame(frame2, bg=results_bg_color, bd=0)  # frame containing tools in the box
tools_frame.grid(row=1, sticky="NEWS", padx=50, pady=25)


# TAB3

buttons_frame = tk.Frame(frame3, bg=main_bg_color)
buttons_frame.grid(row=2)

find_me_button = ttk.Button(buttons_frame, text="FIND ME", padding=[25,10], command=find_me)
find_me_button.grid(row=0, column=0, sticky='s', pady=25)

new_pos_button = ttk.Button(buttons_frame, text="NEW POSITION", padding=[25,10], command=new_pos)
new_pos_button.grid(row=0, column=1, sticky='s', pady=25)

map_widget = tkintermapview.TkinterMapView(frame3, width=800, height=600, corner_radius=0)
map_widget.grid(row=0, sticky='news', padx=50, pady=50)


object_lost_alert = tk.Label(frame3, text="OBJECT LOST", bg="red", font=text_font, padx=50, pady=20)
object_lost_alert.grid(row=1, pady=15)
object_lost_alert.grid_forget()

def refresh():
    connectionStatus, toolsList, errorList = box.update()
    

    if connectionStatus['Status']:
       
        # TAB 1

        # update led
        box_label_led_green = tk.Label(connection_frame, text="In", bg="green", font=text_font, padx=25)
        box_label_led_green.grid(row=0, column=1, sticky="we", padx=25)

        # update error logv
        frame_row = 0
        errors_list = errorList
        if len(errors_list) > 5:
            errors_list = errors_list[-5:]
        if len(errors_list) > 0:
            for e in errors_list:
                
                if e['ErrorType'] in ["MQTT","REST"]:
                    color = warning_text_color
                else:
                    color = error_text_color
                
                result_label = tk.Label(errors_frame,
                                        text=(e['ErrorTime'] +  "  #  " + e['ErrorType'] + ": " + e['ErrorString'] + "\n"),
                                        bg=results_bg_color,
                                        font=("Tw Cen MT", 20), fg=color, anchor='w')
                frame_row += 1
                result_label.grid(row=frame_row, column=0, sticky="WE", pady=5, padx=10)


        # TAB 2

        frame_row = 0
        tools_list = toolsList
        for widget in tools_frame.winfo_children():
            widget.destroy()
        if len(tools_list) > 0:
            n_tools_showed = 0
            for t in tools_list:
                frame_row += 1
                result_label = tk.Label(tools_frame,
                                        text=(t['ToolString'] + "\n"), bg=results_bg_color,
                                        font=("Arial", 20), fg=warning_text_color, anchor='w')
                result_label.grid(row=frame_row, column=0, sticky="WE", pady=5, padx=10)

                if t['Status']:
                    tool_led_green = tk.Label(tools_frame, text="In", bg="green", font=text_font, padx=25)
                    tool_led_green.grid(row=frame_row, column=1, sticky="we", padx=25)
                else:
                    tool_led_red = tk.Label(tools_frame, text="Out", bg="red", font=text_font, padx=25)
                    tool_led_red.grid(row=frame_row, column=1, padx=25)

                n_tools_showed += 1
                if (n_tools_showed == 10):
                    break


        # TAB 3

        map_widget.delete_all_marker()
        refresh.last_position, refresh.lost_tools = box.getPositionAndLostObjectsPositions(new_pos.i)

        if len(refresh.lost_tools) == 0:
            map_widget.set_position(refresh.last_position['Long'], refresh.last_position['Lat'])
            if refresh.object_lost_label_exists:
                object_lost_alert.grid_forget()
                refresh.object_lost_label_exists = False

        for tool in refresh.lost_tools:
            map_widget.set_marker(tool['Long'], tool['Lat'], text=tool['Name'],  marker_color_outside="blue", marker_color_circle="black")
            object_lost_alert.grid()
            refresh.object_lost_label_exists = True

        #map_widget.set_position(refresh.last_position['Long'], refresh.last_position['Lat'])
        map_widget.set_marker(refresh.last_position['Long'], refresh.last_position['Lat'], text='BOX POSITION')
        
        find_me_button['state'] = 'normal'
    else:

        # TAB 1

        box_label_led_red = tk.Label(connection_frame, text="Out", bg="red", font=text_font, padx=25)
        box_label_led_red.grid(row=0, column=1, padx=25)


        # TAB 3

        #map_widget.set_position(refresh.last_position['Long'], refresh.last_position['Lat'])
        map_widget.delete_all_marker()

        if len(refresh.lost_tools) == 0:
            map_widget.set_position(refresh.last_position['Long'], refresh.last_position['Lat'])
            if refresh.object_lost_label_exists:
                object_lost_alert.grid_forget()
                refresh.object_lost_label_exists = False

        for tool in refresh.lost_tools:
            map_widget.set_marker(tool['Long'], tool['Lat'], text=tool['Name'],  marker_color_outside="blue", marker_color_circle="black")
            object_lost_alert.grid()
            refresh.object_lost_label_exists = True
        
        map_widget.set_marker(refresh.last_position['Long'], refresh.last_position['Lat'], text='BOX POSITION')

        find_me_button['state'] = 'disabled'

    window.after(1000, refresh)

refresh.last_position = {'Long': 41.90278, 'Lat': 12.49636}  # default, initialization
refresh.lost_tools = []
refresh.object_lost_label_exists = False

if __name__ == "__main__":
    if platform.system() == 'Windows':
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    window.after(1000, refresh)
    window.mainloop()