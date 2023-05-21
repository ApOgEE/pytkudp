#!/usr/bin/env python3
# Author: M. Fauzilkamil Zainuddin

from threading import Thread
import socket
import select
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class Penerima(Thread):
    def __init__(self, sock, app):
        # Panggil Thread constructor
        self.app = app
        super().__init__()
        self.sock = sock 
        self.jalan_terus = True

    def stop(self):
        # Panggil dari thread lain untuk hentikan penerima
        self.jalan_terus = False

    def bind(self, ip, port):
        self.sock.bind((ip, int(port)))

    def run(self):
        # fungsi ni akan jalan bila method .start dipanggil
        while self.jalan_terus:
            # kita guna select supaya kita tak keras kejung kat recvfrom.
            # kita bangun setiap .5 saat untuk check jalan_terus ke tak
            rfds, _wfds, _xfds = select.select([self.sock], [], [], 0.5)
            if self.sock in rfds:
                try:
                    # terima data
                    data, addr = self.sock.recvfrom(1024)
                    self.app.terima_mesej(data, addr)
                except socket.error as err:
                    print("Error dari socket penerima {}".format(err))
                    break

class Mesej:
    def __init__(self) -> None:
        self.penerima = None
        self.sock = None
        # default config
        config = {
            'localport': '4001',
            'remoteip': '127.0.0.1',
            'remoteport': '4002',
            'mesej_default': 'contoh mesej saya'
        }

        self.setup_gui(config)

    def clearkanMesej(self):
        self.lstMasuk.delete(0,tk.END)

    def terima_mesej(self, data, addr):
        ip, port = addr
        strmesej = data.decode()
        mesej = '{}:{} - {}'.format(ip,port,strmesej)
        self.lstMasuk.insert(0,mesej)

    def mainloop(self, *args):
        self.root.mainloop(*args)

        if self.penerima:
            self.penerima.stop()

    def hantarMesej(self):
        mesej = self.Mesej.get()
        if len(mesej) > 0:
            # menghantar packet udp kepada ip dan port
            ip = self.RemoteIP.get()
            port = int(self.RemotePort.get())

            if self.TambahBaris.get():
                # tambah linefeed
                mesej = '{}\n'.format(mesej)

            remoteAddress = (ip, port)
            byteMesej = str.encode(mesej)
            if self.sock is None:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # hantar mesej
            udpsender = self.sock
            udpsender.sendto(byteMesej, remoteAddress)

            # clearkan socket
            if self.penerima is None:
                self.sock.close()
                self.sock = None


    def toggleBind(self):
        if self.penerima is None:
            # kalau belum bind, set bind dan toggle butang kepada stop
            if self.sock is None:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            try:
                self.penerima = Penerima(self.sock, self)
                self.penerima.bind(self.RemoteIP.get(), int(self.LocalPort.get()))
                self.penerima.start()
                self.btnBind.config(text='Stop')
            except socket.error as err:
                messagebox.showerror('Socket Error', '{} - {}'.format(err.errno, err.strerror))
                self.penerima = None
        else:
            # kalau dah bind, stop thread penerima
            if self.penerima:
                self.penerima.stop()
                self.penerima.join()

            # toggle butang kepada bind dan hapuskan socket
            self.btnBind.config(text='Bind')
            self.penerima = None
            self.sock.close()
            self.sock = None

    def setup_gui(self, cfg):
        # setup GUI tkinter
        self.root = tk.Tk()
        self.root.title('Mesej UDP Menggunakan Python - oleh APOGEE')
        im = Image.open('apogeek.ico')
        photo = ImageTk.PhotoImage(im)
        self.root.wm_iconphoto(True, photo)

        # setup var
        self.LocalPort = tk.StringVar(self.root, value=cfg['localport'])
        self.RemoteIP = tk.StringVar(self.root, value=cfg['remoteip'])
        self.RemotePort = tk.StringVar(self.root, value=cfg['remoteport'])
        self.Mesej = tk.StringVar(self.root, value=cfg['mesej_default'])
        self.TambahBaris = tk.IntVar(self.root, value=0)

        # setup frame
        frm = tk.Frame(self.root)
        lf1 = tk.LabelFrame(frm, text="UDP Config")
        lf1.grid(row=0,column=0, padx=10,pady=10)
        lblLocalPort = tk.Label(lf1, text='Local Port:')
        lblLocalPort.grid(row=0,column=1,padx=10,pady=10)
        txtLocalPort = tk.Entry(lf1, width=8, textvariable=self.LocalPort)
        txtLocalPort.grid(row=0,column=2, padx=(0,10), pady=10)
        lblRemoteIP = tk.Label(lf1, text='Remote IP:')
        lblRemoteIP.grid(row=0,column=3,padx=10, pady=10)
        txtRemoteIP = tk.Entry(lf1, width=15, textvariable=self.RemoteIP)
        txtRemoteIP.grid(row=0,column=4, padx=(0,10), pady=10)
        lblRemotePort = tk.Label(lf1, text='Remote Port:')
        lblRemotePort.grid(row=0,column=5,padx=10, pady=10)
        txtRemotePort = tk.Entry(lf1, width=8, textvariable=self.RemotePort)
        txtRemotePort.grid(row=0,column=6, padx=(0,10), pady=10)
        self.btnBind = tk.Button(lf1, width=10, text="Bind", command=self.toggleBind)
        self.btnBind.grid(row=0,column=7,padx=10,pady=10)
        lf2 = tk.LabelFrame(frm, text="Mesej")
        lf2.grid(row=1,column=0, padx=10,pady=(0,10),sticky='we')
        txtMesej = tk.Entry(lf2, width=60, textvariable=self.Mesej)
        txtMesej.grid(row=0,column=0,padx=10,pady=10)
        chkNewline = tk.Checkbutton(lf2, text='Tambah Newline', variable=self.TambahBaris)
        chkNewline.grid(row=1,column=0,padx=10,pady=(0,10),sticky='w')
        frm2 = tk.Frame(frm)
        frm2.columnconfigure(0, weight=2)
        self.lstMasuk = tk.Listbox(frm2,height=20)
        scroll = tk.Scrollbar(frm2)        
        self.lstMasuk.config(yscrollcommand=scroll.set)
        scroll.config(command=self.lstMasuk.yview)
        self.lstMasuk.grid(row=0, column=0, padx=(10,0),pady=(0,10),sticky='we')
        scroll.grid(row=0, column=1, padx=(0,10),pady=(0,10), sticky='nse')

        frm2.grid(row=2,column=0,sticky='nwse')
        btnHantar = tk.Button(lf2, text='Hantar',command=self.hantarMesej)
        btnHantar.grid(row=0,column=1,padx=(0,10),pady=10, sticky='e')
        btnClear = tk.Button(lf2, text='Clear List', command=self.clearkanMesej)
        btnClear.grid(row=1,column=1,padx=(0,5),pady=10, sticky='e')
        frm.pack(expand=True)

def utama():
    app = Mesej()
    app.mainloop()


if __name__ == '__main__':
    utama()
