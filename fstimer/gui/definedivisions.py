#fsTimer - free, open source software for race timing.
#Copyright 2012-17 Ben Letham

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#The author/copyright holder can be contacted at bletham@gmail.com
'''Handling of the window where divisions are defined'''

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import fstimer.gui
from fstimer.gui.util_classes import GtkStockButton

class DivisionsWin(Gtk.Window):
    '''Handling of the window where divisions are defined'''

    def __init__(self, fields, fieldsdic, divisions, back_clicked_cb,
                 next_clicked_cb, parent, edit):
        '''Creates divisions window'''
        super(DivisionsWin, self).__init__(Gtk.WindowType.TOPLEVEL)
        self.divisions = divisions
        self.fields = fields
        self.fieldsdic = fieldsdic
        self.winnewdiv = None
        self.modify_bg(Gtk.StateType.NORMAL, fstimer.gui.bgcolor)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title('fsTimer - Divisions')
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(20)
        self.set_size_request(800, 500)
        self.connect('delete_event', lambda b, jnk_unused: self.hide())
        # Now create the vbox.
        vbox = Gtk.VBox(False, 10)
        self.add(vbox)
        # Now add the text.
        label2_0 = Gtk.Label(
            "Specify the divisions for reporting divisional places.\n"
            "Press 'Forward' to continue with the default settings, or make "
            "edits below.\n\nDivisions can be any combination of number entry"
            " and selection box fields.")
        # Make the liststore, with columns:
        # name | (... combobox and entrybox_int fields...)
        # To do this we first count the number of fields
        ndivfields = len([field for field in fields
                          if fieldsdic[field]['type']
                          in ['combobox', 'entrybox_int']])
        self.divmodel = Gtk.ListStore(*[str for i_unused
                                        in range(ndivfields + 1)])
        #We will put the liststore in a treeview
        self.divview = Gtk.TreeView()
        #Add each of the columns
        Columns = {}
        Columns[1] = Gtk.TreeViewColumn(
            'Division name', Gtk.CellRendererText(), text=0)
        self.divview.append_column(Columns[1])
        # The fields
        textcount = 1
        for field in fields:
            if fieldsdic[field]['type'] in ['combobox', 'entrybox_int']:
                Columns[field] = Gtk.TreeViewColumn(
                    field, Gtk.CellRendererText(), text=textcount)
                textcount += 1
                self.divview.append_column(Columns[field])
        #Now we populate the model with the default fields
        divmodelrows = {}
        for div in self.divisions:
            divmodelrow = self.get_divmodelrow(div)
            self.divmodel.append(divmodelrow)
        #Done there.
        self.divview.set_model(self.divmodel)
        selection = self.divview.get_selection()
        #And put it in a scrolled window, in an alignment
        divsw = Gtk.ScrolledWindow()
        divsw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        divsw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        divsw.add(self.divview)
        divalgn = Gtk.Alignment.new(0, 0, 1, 1)
        divalgn.add(divsw)
        #Now we put the buttons on the side.
        vbox2 = Gtk.VBox(False, 10)
        btnUP = GtkStockButton('up','Up')
        btnUP.connect('clicked', self.div_up, selection)
        vbox2.pack_start(btnUP, False, False, 0)
        btnDOWN = GtkStockButton('down','Down')
        btnDOWN.connect('clicked', self.div_down, selection)
        vbox2.pack_start(btnDOWN, False, False, 0)
        btnEDIT = GtkStockButton('edit','Edit')
        btnEDIT.connect('clicked', self.div_edit, selection)
        vbox2.pack_start(btnEDIT, False, False, 0)
        btnREMOVE = GtkStockButton('remove','Remove')
        btnREMOVE.connect('clicked', self.div_remove, selection)
        vbox2.pack_start(btnREMOVE, False, False, 0)
        btnNEW = GtkStockButton('new','New')
        btnNEW.connect('clicked', self.div_new, ('', {}), None)
        vbox2.pack_start(btnNEW, False, False, 0)
        btnCOPY = GtkStockButton('copy','Copy')
        btnCOPY.connect('clicked', self.div_copy, selection)
        vbox2.pack_start(btnCOPY, False, False, 0)
        #And an hbox for the fields and the buttons
        hbox4 = Gtk.HBox(False, 0)
        hbox4.pack_start(divalgn, True, True, 10)
        hbox4.pack_start(vbox2, False, False, 0)
        ##And an hbox with 3 buttons
        hbox3 = Gtk.HBox(False, 0)
        btnCANCEL = GtkStockButton('close', 'Close')
        btnCANCEL.connect('clicked', lambda btn: self.hide())
        alignCANCEL = Gtk.Alignment.new(0, 0, 0, 0)
        alignCANCEL.add(btnCANCEL)
        btnBACK = GtkStockButton('back', 'Back')
        if edit:
            btnBACK.set_sensitive(False)
        else:
            btnBACK.connect('clicked', back_clicked_cb)
        btnNEXT = GtkStockButton('forward', 'Next')
        btnNEXT.connect('clicked', next_clicked_cb, edit)
        ##And populate
        hbox3.pack_start(alignCANCEL, True, True, 0)
        hbox3.pack_start(btnBACK, False, False, 2)
        hbox3.pack_start(btnNEXT, False, False, 0)
        alignText = Gtk.Alignment.new(0, 0, 0, 0)
        alignText.add(label2_0)
        vbox.pack_start(alignText, False, False, 0)
        vbox.pack_start(hbox4, True, True, 0)
        vbox.pack_start(hbox3, False, False, 10)
        self.show_all()

    def div_up(self, jnk_unused, selection):
        '''handles a click on UP button'''
        model, treeiter1 = selection.get_selected()
        if treeiter1:
            row = self.divmodel.get_path(treeiter1)
            row = row[0]
            if row > 0:
                # this isn't the bottom item, so we can move it up.
                treeiter2 = model.get_iter(row - 1)
                self.divmodel.swap(treeiter1, treeiter2)
                (self.divisions[row], self.divisions[row - 1]) = (
                    self.divisions[row - 1], self.divisions[row])
        return

    def div_down(self, jnk_unused, selection):
        '''handles a click on DOWN button'''
        model, treeiter1 = selection.get_selected()
        if treeiter1:
            row = self.divmodel.get_path(treeiter1)
            row = row[0]
            if row < len(self.divisions) - 1:
                #this isn't the bottom item, so we can move it down.
                treeiter2 = model.get_iter(row + 1)
                self.divmodel.swap(treeiter1, treeiter2)
                (self.divisions[row], self.divisions[row + 1]) = (
                    self.divisions[row + 1], self.divisions[row])
        return

    def div_edit(self, jnk_unused, selection):
        '''handles a click on EDIT button'''
        treeiter1 = selection.get_selected()[1]
        if treeiter1:
            row = self.divmodel.get_path(treeiter1)
            row = row[0]
            self.div_new(None, self.divisions[row], treeiter1)
        return

    def div_new(self, jnk_unused, divtupl, treeiter):
        '''handles a click on NEW button'''
        self.winnewdiv = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.winnewdiv.modify_bg(Gtk.StateType.NORMAL, fstimer.gui.bgcolor)
        self.winnewdiv.set_transient_for(self)
        self.winnewdiv.set_modal(True)
        self.winnewdiv.set_title('fsTimer - New division')
        self.winnewdiv.set_position(Gtk.WindowPosition.CENTER)
        self.winnewdiv.set_border_width(20)
        self.winnewdiv.connect(
            'delete_event', lambda b, jnk_unused: self.winnewdiv.hide())
        #Prepare for packing.
        vbox = Gtk.VBox(False, 10)
        windescr = Gtk.Label(
            'Use the checkboxes to select which fields to use to define this '
            'division,\nand then select the corresponding value to be used '
            'for this division.')
        vbox.pack_start(windescr, False, False, 0)
        HBoxes = {}
        CheckButtons = {}
        ComboBoxes = {}
        minadjs = {}
        minbtns = {}
        maxadjs = {}
        maxbtns = {}
        #Process the input
        divnamein = divtupl[0]
        divdic = divtupl[1]
        #First name of the divisional.
        divnamelbl = Gtk.Label(label='Division name:')
        divnameentry = Gtk.Entry()
        divnameentry.set_max_length(80)
        divnameentry.set_width_chars(40)
        divnameentry.set_text(divnamein)  # set to initial value
        HBoxes[1] = Gtk.HBox(False, 10)  # int key won't collide with a field
        HBoxes[1].pack_start(divnamelbl, False, False, 0)
        HBoxes[1].pack_start(divnameentry, False, False, 0)
        vbox.pack_start(HBoxes[1], False, False, 0)
        #And now all of the fields
        for field in self.fields:
            if self.fieldsdic[field]['type'] == 'combobox':
                #Add it.
                CheckButtons[field] = Gtk.CheckButton(label=field + ':')
                ComboBoxes[field] = Gtk.ComboBoxText()
                for option in self.fieldsdic[field]['options']:
                    ComboBoxes[field].append_text(option)
                    if field in divdic and divdic[field]:
                        CheckButtons[field].set_active(True)  # check box
                        ComboBoxes[field].set_active(
                            self.fieldsdic[field]['options'].index(
                                divdic[field]))
                #Put it in an HBox
                HBoxes[field] = Gtk.HBox(False, 10)
                HBoxes[field].pack_start(CheckButtons[field], False, False, 0)
                HBoxes[field].pack_start(ComboBoxes[field], False, False, 0)
                vbox.pack_start(HBoxes[field], False, False, 0)
            elif self.fieldsdic[field]['type'] == 'entrybox_int':
                CheckButtons[field] = Gtk.CheckButton(label=field + ':')
                if field in divdic:
                    CheckButtons[field].set_active(True)
                    minadjs[field] = Gtk.Adjustment(
                        value=divdic[field][0], step_incr=1, lower=-10000, upper=10000)
                    maxadjs[field] = Gtk.Adjustment(
                        value=divdic[field][1], step_incr=1, lower=-10000, upper=10000)
                else:
                    minadjs[field] = Gtk.Adjustment(value=0, step_incr=1,
                                                    lower=-10000, upper=10000)
                    maxadjs[field] = Gtk.Adjustment(value=120, step_incr=1,
                                                    lower=-10000, upper=10000)
                minlbl = Gtk.Label(label='From:')
                minbtns[field] = Gtk.SpinButton(digits=0, climb_rate=0)
                minbtns[field].set_adjustment(minadjs[field])
                maxlbl = Gtk.Label(label='Through:')
                maxbtns[field] = Gtk.SpinButton(digits=0, climb_rate=0)
                maxbtns[field].set_adjustment(maxadjs[field])
                #Make an hbox of it.
                HBoxes[field] = Gtk.HBox(False, 10)
                HBoxes[field].pack_start(CheckButtons[field], False, False, 0)
                HBoxes[field].pack_start(minlbl, False, False, 0)
                HBoxes[field].pack_start(minbtns[field], False, False, 0)
                HBoxes[field].pack_start(maxlbl, False, False, 0)
                HBoxes[field].pack_start(maxbtns[field], False, False, 0)
                vbox.pack_start(HBoxes[field], False, False, 0)
        #On to the bottom buttons
        btnOK = GtkStockButton('ok','OK')
        btnOK.connect('clicked', self.winnewdivOK, treeiter, CheckButtons,
                      ComboBoxes, minbtns, maxbtns, divnameentry)
        btnCANCEL = GtkStockButton('close','Cancel')
        btnCANCEL.connect('clicked', lambda b: self.winnewdiv.hide())
        cancel_algn = Gtk.Alignment.new(0, 0, 0, 0)
        cancel_algn.add(btnCANCEL)
        hbox3 = Gtk.HBox(False, 10)
        hbox3.pack_start(cancel_algn, True, True, 0)
        hbox3.pack_start(btnOK, False, False, 0)
        vbox.pack_start(hbox3, False, False, 0)
        self.winnewdiv.add(vbox)
        self.winnewdiv.show_all()

    def div_remove(self, jnk_unused, selection):
        '''handles a click on REMOVE button'''
        treeiter1 = selection.get_selected()[1]
        if treeiter1:
            row = self.divmodel.get_path(treeiter1)
            row = row[0]
            self.divmodel.remove(treeiter1)
            self.divisions.pop(row)
            selection.select_path((row, ))

    def div_copy(self, jnk_unused, selection):
        '''handles a click on COPY button'''
        treeiter1 = selection.get_selected()[1]
        if treeiter1:
            row = self.divmodel.get_path(treeiter1)
            row = row[0]
            div = self.divisions[row]
            new_name = div[0] + ' (Copy)'
            self.divisions.append([new_name, div[1]])
            #Get the row for the UI
            divmodelrow = self.get_divmodelrow(div, new_name)
            #All done! Add this row in.
            self.divmodel.append(divmodelrow)
            selection.select_path((len(self.divisions), ))
    
    def get_divmodelrow(self, div, name=None):
        # Start with the name
        if name is None:
            divmodelrow = [div[0]]
        else:
            divmodelrow = [name]
        #And then all other columns
        for field in self.fields:
            if self.fieldsdic[field]['type'] == 'combobox':
                if field in div[1]:
                    divmodelrow.append(div[1][field])
                else:
                    divmodelrow.append('')
            elif self.fieldsdic[field]['type'] == 'entrybox_int':
                if field in div[1]:
                    divmodelrow.append(
                        '{} through {}'.format(div[1][field][0],
                                               div[1][field][1]))
                else:
                    divmodelrow.append('')
        return divmodelrow
    
    def winnewdivOK(self, jnk_unused, treeiter, CheckButtons, ComboBoxes,
                    minbtns, maxbtns, divnameentry):
        '''handles a click on OK button'''
        #First get the division name
        div = (divnameentry.get_text(), {})
        #And now go through the fields.
        for field, btn in CheckButtons.items():
            if btn.get_active():
                if field in ComboBoxes and ComboBoxes[field].get_active() > -1:
                    div[1][field] = self.fieldsdic[field]['options'][
                        ComboBoxes[field].get_active()]
                elif field in minbtns:
                    div[1][field] = (minbtns[field].get_value_as_int(),
                                     maxbtns[field].get_value_as_int())
        if treeiter:
            #we are replacing a division
            row = self.divmodel.get_path(treeiter)
            row = row[0]
            self.divisions[row] = div  # replace the old division with the new
            #And now update the divmodel
            self.divmodel.set_value(treeiter, 0, div[0])
            colcount = 1
            for field in self.fields:
                if self.fieldsdic[field]['type'] in ['combobox',
                                                     'entrybox_int']:
                    if field in div[1]:
                        if self.fieldsdic[field]['type'] == 'combobox':
                            self.divmodel.set_value(treeiter, colcount,
                                                    div[1][field])
                        else:
                            self.divmodel.set_value(
                            treeiter, colcount,'{} through {}'.format(
                                div[1][field][0], div[1][field][1]))
                    else:
                        self.divmodel.set_value(treeiter, colcount, '')
                    colcount += 1
        else:
            #no treeiter- this was a new entry.
            #Add it to self.divisions
            self.divisions.append(div)
            divmodelrow = self.get_divmodelrow(div)
            self.divmodel.append(divmodelrow)
        self.winnewdiv.hide()
