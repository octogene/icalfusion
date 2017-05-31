#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Bogdan Cordier
#
# Distributed under terms of the MIT license.

from icalendar import Calendar
from tkinter import Tk, filedialog, Listbox, Button, Entry, StringVar, \
    LabelFrame, BooleanVar, Frame, ttk, END, Checkbutton, messagebox

ical_fields = ('SUMMARY', 'UID', 'LOCATION', 'CATEGORIES', 'DTSTART', 'DTEND')


class GUI:
    def __init__(self):
        self.root = Tk()
        self.root.title('ICal Fusion')
        self.root.iconbitmap('@icon.xbm')
        self.create_filter_frame()
        self.files = []
        self.create_files_list_frame()
        self.create_duplicates_frame()
        self.btn_frame = Frame(self.root)
        self.create_button_frame()
        self.calendar = Calendar()
        self.root.mainloop()

    def create_filter_frame(self):
        filter_frame = LabelFrame(self.root, text='Filter')
        self.filter_type = ttk.Combobox(filter_frame, values=ical_fields)
        self.filter_type.current(0)
        self.filter_type.bind("<<ComboboxSelected>>", self.update_filter_cond)
        self.filter_type.state(('!disabled', 'readonly'))
        self.filter_type.grid(row=0)

        self.filter_cond = ttk.Combobox(filter_frame,
                                        values=('CONTAINS',
                                                'EQUAL TO'))
        self.filter_cond.current(0)
        self.filter_cond.state(('!disabled', 'readonly'))
        self.filter_cond.grid(row=0, column=1)

        self.filter_value = StringVar()

        self.filter_entry = Entry(filter_frame,
                                  textvariable=self.filter_value,
                                  width=25,
                                  bg='white')
        self.filter_entry.grid(row=0, column=2)
        filter_frame.pack(fill='x', side='top')

    def update_filter_cond(self, *args):
        """ Update filter conditions on filter type selection.
        """

        if self.filter_type.get() in ('DTSTART', 'DTEND'):
            self.filter_cond['values'] = ('BEFORE', 'AFTER', 'EQUAL TO')

        else:
            self.filter_cond['values'] = ('CONTAINS', 'EQUAL TO')

        self.filter_cond.current(0)



    def create_files_list_frame(self):
        files_list_frame = LabelFrame(self.root, text='Files to merge')
        self.FilesList = Listbox(files_list_frame)
        self.FilesList.pack(side='left', fill='both', expand=1)
        files_list_frame.pack(fill='x')

    def create_duplicates_frame(self):
        frame = Frame(self.root)
        self.duplicates_check = BooleanVar()
        self.duplicates_filter = ttk.Combobox(frame, value=ical_fields)
        self.duplicates_filter.current(0)
        self.duplicates_filter.state(('!disabled', 'readonly'))
        self.duplicates_filter.pack(side='right')
        self.duplicates_cbox = Checkbutton(frame,
                                           variable=self.duplicates_check,
                                           text='Remove duplicates by')
        self.duplicates_cbox.pack(side='right')
        frame.pack(fill='x')

    def create_button_frame(self):
        Button(self.btn_frame, text='Add...',
               command=self.add_files).grid(row=0, column=0)
        Button(self.btn_frame, text='Merge',
               command=self.join_files).grid(row=0, column=1)
        self.btn_frame.pack(side='bottom')

    def add_files(self):
        files = filedialog.askopenfilenames(title="Load ICal files",
                                            filetypes=[('ICal files', '.ics'),
                                                       ('all files', '.*')])
        for file in files:
            self.FilesList.insert(END, file)

    def filter(self, event):
        value = self.filter_value.get()
        field = self.filter_type.get()
        if self.filter_cond.get() == 'CONTAINS':
            if value in event.get(field):
                return True
        if self.filter_cond.get() == 'EQUAL TO':
            if value == event.get(field):
                return True

        return False

    def join_files(self):
        if self.FilesList.get(0, END):
            ical = filedialog.asksaveasfilename(title='Save as...')
            self.checked_values = set()

            for file in self.FilesList.get(0, END):
                ics = open(file, 'r')
                cal = Calendar.from_ical(ics.read())
                ics.close()
                events = (co for co in cal.walk() if co.name == 'VEVENT')
                for event in events:
                    if self.duplicates_check.get():
                        field = self.duplicates_filter.get()
                        value = event.get(field)
                        if value in self.checked_values:
                            break
                        else:
                            self.checked_values.add(value)

                    if self.filter_value:
                        if self.filter(event):
                            self.calendar.add_component(event)
                    else:
                        if self.duplicates_cbox.getboolean():
                            pass
                        else:
                            self.calendar.add_component(event)

            with open(ical, 'wb') as f:
                f.write(self.calendar.to_ical())

            messagebox.showinfo('Success', 'Files were successfully joined !')
        else:
            messagebox.showerror('No files', 'Please add files to merge...')

if __name__ == '__main__':
    GUI()
