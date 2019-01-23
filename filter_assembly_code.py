"""
MIT License

Copyright (c) 2019 C. Claus 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import clr
import sys
from random import random
from random import randint
from math import *
from collections import OrderedDict
import itertools



clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
clr.AddReference("RevitAPI") 
clr.AddReference("RevitAPIUI")

import Autodesk
from Autodesk.Revit.DB import * 
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.Exceptions import InvalidOperationException


import System
from System.Collections.Generic import *
from System.Collections import *
from System import *
from System.Drawing import Point, Icon, Color
from System.Drawing import Color, Font, FontStyle, Point
from System.Windows.Forms import (Application, BorderStyle, FormBorderStyle, Button, CheckBox, Form, Label, Panel, ToolTip, RadioButton, CheckedListBox, CheckState, PictureBox)
from System.Drawing import Icon



app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document
view = doc.ActiveView

#__window__.Hide()
#__window__.Close()

#CAUTION: RAILINGS ARE NOT ENCLOSED IN ASSEMBLY CODE FILTER
######################################################################################################
################################## Get Built in Categories ###########################################
######################################################################################################
categories_list = [    
                                'OST_Walls',
                                'OST_Floors',
                                'OST_Ceilings',
                                'OST_StructuralFraming',
                                'OST_StructuralFoundation',
                                'OST_StructuralColumns',
                                'OST_Roofs', 
                                'OST_Ramps',
                                'OST_Stairs',
                                'OST_Site',
                                'OST_DuctTerminal', 
                                'OST_Casework',
                                'OST_CableTray',
                                'OST_Conduit', 
                                'OST_ElectricalFixtures',
                                'OST_Furniture',
                                'OST_Gutter',
                                'OST_GenericModel',
                                'OST_MechanicalEquipment',
                                'OST_PlumbingFixtures',
                                'OST_Doors',
                                'OST_Windows',
                                'OST_CurtainWallMullions',
                                'OST_CurtainWallPanels',
                                'OST_RailingBalusterRail',
                                'OST_RailingBalusterRailCut',
                                'OST_RailingHandRail',
                                'OST_RailingHandRailAboveCut',
                                'OST_Railings',
                                'OST_RailingSystem',
                                'OST_RailingsystemBaluster'
                                ]  
        
builtin_categories = System.Enum.GetValues(BuiltInCategory)

t1, t2 = [],[]
categories_assembly_code_list = []

for category, builtin_category in [(category,builtin_category) for category in categories_list for builtin_category in builtin_categories]:
    if category == builtin_category.ToString():
        t1.append(FilteredElementCollector(doc).WhereElementIsNotElementType().OfCategory(builtin_category).ToElements())
        t2.append(builtin_category)
        
elements, categories = [], []
categories_list = []

for i in range(len(t1)):
    if t1[i]:
        elements.append(t1[i])
        categories.append(t2[i])
        
for i in elements:
    for j in i:
        categories_list.append(j)


######################################################################################################
############################### Get Type Parameter Assembly Code #####################################
######################################################################################################
id_assembly_dict = {}
assembly_code_list = []

ac_list = []
ad_list = []
ac_ad_list = []

empty_list = []
id_empty_dict = {}


for i in categories_list:

	element_type = doc.GetElement(i.GetTypeId())
	parameters = element_type.Parameters
	
	if element_type.LookupParameter('Assembly Code').AsString():
		assembly_code = element_type.LookupParameter('Assembly Code').AsString()
		categories_assembly_code_list.append(assembly_code)
		id_assembly_dict[doc.GetElement(i.Id)] = assembly_code , element_type.LookupParameter('Assembly Description').AsString()
	if element_type.LookupParameter('Assembly Code'):
		empty_assembly_code = element_type.LookupParameter('Assembly Code').AsString()
		id_empty_dict[doc.GetElement(i.Id)] = empty_assembly_code


for key, value in sorted(id_assembly_dict.iteritems(), key=lambda (k,v): (v,k)):
	#print "%s: %s" % (key, value)
	ac_list.append(value[0])
	ac_ad_list.append([value[0], value[1]])
	

sorted_ac_list = sorted(set(ac_list))

ac_ad_list.sort()

sorted_list =  list(ac_ad_list for ac_ad_list, _ in itertools.groupby(ac_ad_list))




######################################################################################################
############################### Graphical User Interface Class #######################################
######################################################################################################
width = 500
height = 990


class AssemblyFilter(IExternalEventHandler, Form):
    def __init__(self):
        
        self.check_value = []
        self.selected_code_list = []
        
        self.BorderStyle = BorderStyle.Fixed3D
        self.Width = width
        self.Height = height
        self.Text = "Assembly Code Filter | Version 2.0 | 2019 "
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.FixedDialog
        
        
        self.Controls.Add(self.header(0,0))
        self.Controls.Add(self.panel(0,80))
        self.Controls.Add(self.footer(0,930))

    
    def header(self, x, y):
        
        style = FontStyle.Bold 

        assembly_codes_selected = '-'
        objects_selected = '-'
        
        self.sublabel = Label()
        self.sublabel.Text = "Number of Assembly Codes Selected: " + str(assembly_codes_selected)
        self.sublabel.Location = Point(x+40, y+10)
        self.sublabel.Width = width-200
        self.sublabel.Font = Font("Calibri Light", 12) 
        #self.sublabel.ForeColor = Color.White
        self.sublabel.ForeColor = Color.Black
        
        self.sublabel_objects = Label()
        self.sublabel_objects.Text = "Number of Objects Current Selection: " + str(objects_selected)
        self.sublabel_objects.Location = Point(x+40, y+30)
        self.sublabel_objects.Width = width-200
        self.sublabel_objects.Font = Font("Calibri Light", 12) 
        #self.sublabel_objects.ForeColor = Color.White
        self.sublabel.ForeColor = Color.Black
        
        self.sublabel_no_selection = Label()
        self.sublabel_no_selection.Text = ""
        self.sublabel_no_selection.Location = Point(x+40, y+50)
        self.sublabel_no_selection.Width = width-200
        self.sublabel_no_selection.Font = Font("Calibri Light", 12, style)
        #self.sublabel_no_selection.ForeColor = Color.White 
        self.sublabel.ForeColor = Color.Black
        
        self.header = Panel()
        self.header.Width = width
        self.header.Height = 80
        self.header.AutoSize = True
        self.header.Font = Font("Calibri", 12) 
        self.header.Location = Point(x,y)
        #self.header.BackColor = Color.FromArgb(0, 0, 0)
        self.header.BackColor = Color.FromArgb(145, 201, 213)

        self.header.Controls.Add(self.sublabel)
        self.header.Controls.Add(self.sublabel_objects)
        self.header.Controls.Add(self.sublabel_no_selection)
        self.header.AutoScroll = True

    
        return self.header
        
    def panel(self, x, y):
    
        self.panel = Panel()
        self.panel.Width = width-15
        self.panel.Height = 800
        self.panel.Location = Point(x, y)
        self.panel.BorderStyle = BorderStyle.Fixed3D
        self.panel.BackColor = Color.White
        self.panel.AutoScroll = True
        
        j=30
   
        for i in sorted_list:
        
        	self.checkbox = CheckBox()
        	self.checkbox.Text = i[0] 
        	self.checkbox.Location = Point(35,j)
        	self.checkbox.Font = Font("Calibri Light", 10)
        	
        	self.checkbox_description = Label()
        	self.checkbox_description.Text = i[1]
        	self.checkbox_description.Location = Point(150,j+2)
        	self.checkbox_description.Width = 500
        	
        	self.checkbox_description.Font = Font("Calibri Light", 10)
        	self.panel.Controls.Add(self.checkbox)
        	self.panel.Controls.Add(self.checkbox_description)
        	self.check_value.append(self.checkbox)
        	
        	j += 25
        
        
        return self.panel	
  
            
    def footer(self, x, y):

        button_width = (width/3)-6
        
        self.button_filter_selection = Button()
        self.button_filter_selection.Text = 'Filter Selection'
        self.button_filter_selection.Location = Point(2*(button_width),0)
        self.button_filter_selection.Click += self.update
        self.button_filter_selection.Width = button_width
        self.button_filter_selection.Height = 50
        
        self.button_clear_selection = Button()
        self.button_clear_selection.Text = 'Clear Selection'
        self.button_clear_selection.Location = Point(0,0)
        self.button_clear_selection.Width = button_width
        self.button_clear_selection.Height = 50
        self.button_clear_selection.Font =  Font("Calibri Light",12)
        self.button_clear_selection.Click += self.uncheck_checkboxes
        
        self.button_objects_without_code = Button()
        self.button_objects_without_code.Text = 'Objects Without Assembly Code'
        self.button_objects_without_code.Location = Point(button_width,0)
        self.button_objects_without_code.Width = button_width
        self.button_objects_without_code.Height = 50
        self.button_objects_without_code.Click += self.check_pushbutton_empty_assembly_code
        
        self.footer = Panel()
        self.footer.Width = width-15
        self.footer.Height = 50
        self.footer.Font = Font("Calibri", 12) 
        self.footer.Location = Point(x,y-50)
        #self.footer.BackColor = Color.FromArgb(232, 52, 38)
        self.footer.Controls.Add(self.button_filter_selection)
        self.footer.Controls.Add(self.button_clear_selection)
        self.footer.Controls.Add(self.button_objects_without_code)


        return self.footer
        


    def update(self, sender, event):
 
        for f in self.check_value:
            if f.Checked == True:
                self.selected_code_list.append(f.Text)
            if f.Checked == False:
                   pass 
         
        self.check_for_selected_code(selected_code=self.selected_code_list)
        
        for f in self.check_value:
            if f.Text in self.selected_code_list:
                self.selected_code_list.remove(f.Text)
                       

                   
    def uncheck_checkboxes(self, sender, event):

        
        self.sublabel_no_selection.Text = ""
        
        for f in self.check_value:
            f.Checked = False
            
        t = Transaction(doc, 'Reset HideIsolate')    
        t.Start()        
        view.TemporaryViewModes.DeactivateAllModes()
        t.Commit()    
        
        assembly_codes_selected = '-'
        objects_selected = '-'

        self.sublabel.Text = "Number of Assembly Codes Selected: " + str(assembly_codes_selected)
        self.sublabel_objects.Text = "Number of Objects Current Selection: " + str(objects_selected)

        
    def check_pushbutton_empty_assembly_code(self, sender, args):
        self.check_empty_assembly_code(selected_code=sender.Text) 
        
    def check_empty_assembly_code(self, selected_code):
    
        self.sublabel_no_selection.Text = ""
  
        ids = list()

        element_instances = []

        for i, v in id_empty_dict.iteritems():
        	if len(v) == 0:
        		element_instances.append(i.Id)
        		ids.append(i.Id)
                    
        self.sublabel_objects.Text = "Number of Objects Current Selection: " + str(len(ids))
        assembly_codes_selected = '-'
        self.sublabel.Text = "Number of Assembly Codes Selected: " + str(assembly_codes_selected)
        

        #Hide Reset Active View
        t = Transaction(doc, 'Reset HideIsolate')    
        t.Start()        
        view.TemporaryViewModes.DeactivateAllModes()
        t.Commit()    

        idElements = List[ElementId](ids)
        
        #Hide Isolate Objects in Active View
        t = Transaction(doc, 'Filter Elements')
        t.Start()    
        view.IsolateElementsTemporary(idElements)
        t.Commit()

   
    def check_for_selected_code(self, selected_code):
  
        if len(selected_code) == 0:
        	
        	self.sublabel_no_selection.Text = "Please select an Assembly Code First!"
        
        if len(selected_code) > 0:

	        self.sublabel.Text = "Number of Assembly Codes Selected: " + str(len(selected_code))
	
	        ids = list()
	        
	        for i, v in id_assembly_dict.iteritems():
	        	if len(v) > 1:
	        		for code in selected_code:
	        			if v[0] ==  code:
	        				ids.append(i.Id)
	        			
	                
	        self.sublabel_objects.Text = "Number of Objects Current Selection: " + str(len(ids))
	        
	        #Hide Reset Active View    
	        t = Transaction(doc, 'Reset HideIsolate')    
	        t.Start()
	        view.TemporaryViewModes.DeactivateAllModes()
	        t.Commit()    
	        
	        idElements = List[ElementId](ids)
	        
	        #Hide Isolate Objects in Active View
	        t = Transaction(doc, 'Filter Elements')    
	        t.Start()    
	        view.IsolateElementsTemporary(idElements)
	        t.Commit()
    


form = AssemblyFilter()

#form.BringToFront
#Application.Run(form)
#form.ShowDialog()
#form.BringToFront
external_event = ExternalEvent.Create(form)
Application.Run(form)
#Application.Run(form)


#__window__.Hide()
#__window__.Close()