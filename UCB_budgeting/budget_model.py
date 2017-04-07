import numpy as np
from os.path import dirname, join
from bokeh.plotting import figure , curdoc #show,output_file
import pandas as pd
from bokeh.models.widgets import Slider, Select, TextInput, Panel, Tabs
from bokeh.models import HoverTool, BoxSelectTool, Div

from bokeh.layouts import widgetbox, layout,row, column

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), width=800)
#output_file("budget.html")

SRECNA2 =pd.read_excel('SISD.xlsx')
SRECNA3=SRECNA2.dropna(axis=0,how='all')  #Drops rows with all NaN values
Indexes=list(SRECNA3.index.values)
SRECNA3=SRECNA3.drop([Indexes[8],Indexes[20],Indexes[19],Indexes[18],Indexes[17],Indexes[16],Indexes[15]],axis=0)
Depreciation =pd.read_excel('Income Statement Data v.1.xlsx')
Depreciation=Depreciation.dropna(axis=0,how='all')
indexes=list(Depreciation.index.values)
depreciation=Depreciation.loc[[indexes[17],indexes[18]],:]
depreciation=depreciation.values[:,:-2]
newValues=SRECNA3.values[:,:]
nextYears=np.zeros((newValues.shape[0],newValues.shape[1]-1))
Svalues=np.hstack((newValues,nextYears))
Svalues=np.vstack((Svalues,depreciation))

class Operator:
    """An operator operates on the global set of data  scenario."""

    def __init__(self,data):
        """Create an operator with a given section with the given exit.

        name -- A string; the name of this Place.
        exit -- The Place reached by exiting this Place (may be None).
        """
        self.base_levels=np.array([1.5,2.0,0.0,0.0,2.0,2.0,0.0,1.5,1.5,1.5,0.0,1.5,0.0,0.0])
        self.data=np.copy(data)
        self.years_update=data.shape[1]
    def leveler(self, section, assumption):
        i=4
        while(i < self.years_update):    
            newEntry=self.data[section,i-1]*(1.0+assumption)
            self.data[section,i]=newEntry
            i+=1
        totalRevs=np.sum(self.data[0:8,:],axis=0)
        totalExps=np.sum(self.data[8:-2,:],axis=0)
        depreciation=np.sum(self.data[-2:,:],axis=0)
        new_data=totalRevs-totalExps-depreciation
        return new_data/1000
    #Creates case using base_levels for all operators
    def basecase(self):
        section=0
        initial=self.leveler(0,0) # initialized the first 4 values
        for i in self.base_levels:
            initial[4:]=self.leveler(section,i)[4:]
            section+=1
        return initial
            
years=np.linspace(2014,2020,7) # 4 base years and 3 years being operating one. 7 operating years
operator1=Operator(Svalues)
operator2=Operator(Svalues)
y1=operator1.basecase()
y2=operator2.basecase()
hover = HoverTool(
        tooltips=[
            ("Index", "$index"),
            ("Net Income", "$y")
        ]
    )

TOOLS = [BoxSelectTool(), hover, 'crosshair']
model = figure(title="Budget Model", plot_height=600, plot_width=800,tools=TOOLS) 
r = model.line(years,y1, color="#2222aa", line_width=2,line_dash=[4, 4], legend ="Scenario")
base=model.line(years,y2, line_width=2,legend="Base Case")
#Change background color
model.background_fill_color = "white"
# change just some things about the x-axes
model.xaxis.axis_label = "Years"
model.xaxis.axis_line_width = 2
model.xaxis.axis_line_color = "Black"

# change just some things about the y-axes

model.yaxis.axis_label = "Net Income (Millions)"
model.yaxis.major_label_text_color = "Black"
model.yaxis.major_label_orientation = "horizontal"

# change just some things about the x-grid
model.xgrid.grid_line_color = "Black"
model.xgrid.grid_line_alpha = 0.3
# change just some things about the y-grid
model.ygrid.grid_line_alpha = 0.1
model.ygrid.grid_line_color = "Black"
#Change the outline of the plot box
model.outline_line_width = 10
model.outline_line_alpha = 0.3
model.outline_line_color = "navy"


#Revenues Levelers
Tuition = Slider(title="Tuition (%)", start=-1.5, end=4,step=1.5,value=1.5,callback_policy='mouseup')
State = Slider(title="State (%)",start=-2.0, end=6.0,step=2.0,value=2.0,callback_policy='mouseup')
Pell_grants = Slider(title="Pell Grants (%)",start=-5.0, end=5.0,step=2.5,value=0.0,callback_policy='mouseup')
Contracts = Slider(title="Contracts (%)",start=-5.0, end=5.0,step=2.5,value=0.0,callback_policy='mouseup')
Educational_activities = Slider(title="Educational Activities (%)",start=-2.0, end=6.0,step=2.0, value=2.0,callback_policy='mouseup')
Private_gifts = Slider(title="Private Gifts (%)",start=-2.0, end=6.0,step=2.0,value=2.0,callback_policy='mouseup')
Investment_income = Slider(title="Investment income (%)",start=-10.0, end=10.0,step=5.0,value=0.0,callback_policy='mouseup')
Otherr = Slider(title="Other (%)",start=-1.5, end=4.0,step=1.5,value=1.5,callback_policy='mouseup')

#Expenses Levelers
Salaries = Slider(title="Salaries (%)",start=-1.5, end=4.0,step=1.5,value=1.5,callback_policy='mouseup')
Benefits = Slider(title="Benefits (%)",start=-1.5, end=4.0,step=1.5,value=1.5,callback_policy='mouseup')
Scholarships = Slider(title="Scholarships and Fellowships (%)",start=-5.0, end=5.0,step=2.5,value=0.0,callback_policy='mouseup')
Utilities= Slider(title="Utilities (%)",start=-1.5, end=4.0,step=1.5,value=1.5, callback_policy='mouseup')
Supplies= Slider(title="Supplies (%)",start=-5.0, end=5.0,step=2.5,value=0.0,callback_policy='mouseup')
Othere= Slider(title="Other (%)",start=-5.0, end=5.0,step=2.5,value=0.0,callback_policy='mouseup')

#Interacting widgets for Revenues
def update_tuition(attrname, old, new):
    value = Tuition.value
    new_data=operator1.leveler(0, value)
    r.data_source.data['y'] = new_data
    
    
Tuition.on_change('value', update_tuition)
    
def update_state(attrname, old, new):
    value = State.value
    new_data=operator1.leveler(1, value)
    r.data_source.data['y'] = new_data
    
State.on_change('value', update_state)

def update_pell_grants(attrname, old, new):
    value = Pell_grants.value
    new_data=operator1.leveler(2, value)
    r.data_source.data['y'] = new_data
    
Pell_grants.on_change('value', update_pell_grants)

def update_contracts(attrname, old, new):
    value = Contracs.value
    new_data=operator1.leveler(3, value)
    r.data_source.data['y'] = new_data
Contracts.on_change('value', update_contracts)
    
def update_educational_activities(attrname, old, new):
    value = Educational_activities.value
    new_data=operator1.leveler(4, value)
    r.data_source.data['y'] = new_data
    
Educational_activities.on_change('value', update_educational_activities)


def update_private_gifts(attrname, old, new):
    value =Private_gifts.value
    new_data=operator1.leveler(5,value)
    r.data_source.data['y'] = new_data
    
#Private_gifts.on_change('value', update_private_gifts)

def update_investment_income(attrname, old, new):
    value = Investment_income.value
    new_data=operator1.leveler(6, value)
    r.data_source.data['y'] = new_data
    
#Investment_income.on_change('value', update_investment_income)

def update_otherr(attrname, old, new):
    value= Otherr.value
    new_data=operator1.leveler(7,value )
    r.data_source.data['y'] = new_data
    
#Otherr.on_change('value', update_otherr)

    
#Interacting widgets for expenses

def update_salaries(attrname, old, new):
    value = Salaries.value
    new_data=operator1.leveler(8, value)
    r.data_source.data['y'] = new_data
    
#Salaries.on_change('value', update_salaries)


    
def update_benefits(attrname, old, new):
    value = Benefits.value
    new_data=operator1.leveler(9, value)
    r.data_source.data['y'] = new_data
    
Benefits.on_change('value', update_benefits)


def update_scholarships(attrname, old, new):
    value = Scholarships.value
    new_data=operator1.leveler(10, value)
    r.data_source.data['y'] = new_data
    
Scholarships.on_change('value', update_scholarships)


    
def update_utilities(attrname, old, new):
    value = Utilities.value
    new_data=operator1.leveler(11, value)
    r.data_source.data['y'] = new_data
Utilities.on_change('value', update_utilities)

    
def update_supplies(attrname, old, new):
    value = Supplies.value
    new_data=operator1.leveler(12, value)
    r.data_source.data['y'] = new_data
    
Supplies.on_change('value', update_supplies)


    
def update_othere(attrname, old, new):
    value = Othere.value
    new_data=operator1.leveler(13, value)
    r.data_source.data['y'] = new_data
Othere.on_change('value', update_othere)

revenues=[Tuition,State, Pell_grants,Contracts,Educational_activities,Private_gifts,Investment_income,Otherr]
expenses=[Salaries,Benefits,Scholarships,Utilities,Supplies,Othere]
Revenues= widgetbox(*revenues, sizing_mode='fixed')
Expenses= widgetbox(*expenses, sizing_mode='fixed')
tab1 = Panel(child=Revenues, title="Revenues")
tab2 = Panel(child=Expenses, title="Expenses")
tabs = Tabs(tabs=[ tab1, tab2 ])
l=layout([[desc],
    [tabs,model]], sizing_mode='fixed')
#show(l)

curdoc().add_root(l)   


