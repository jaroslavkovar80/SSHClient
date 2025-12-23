# mapp View / VC4 

The mapp Framework offers the choice between either a mapp View front end or a VC4 front end. Select your preference via the dropdown in the import tool.You can also select to import no visualization and just get the backend code. 

The mapp View visualization supports a modular import. You will only get the visualization files for the framework components that you choose to import. 
On the contrary, the VC4 visualization is all-or-nothing. In other words, if you import just mapp AlarmX and select the VC4 front end, the VC4 visualization will include pages for ALL available framework components. You will then need to delete the VC4 pages that are not relevant to you. 



Interface to the HMI

Each mapp Framework has a structure variable for commands, parameters, and status information from the HMI. This variable name always starts with "Hmi" followed by the mapp Technology (e.g. HmiRecipe). 
Note: The only exception is the Axis framework, where the HMI is linked directly to the AxisCommands structure. This is because in manual mode the commands come from the HMI, but in automatic mode the commands are triggered directly in the application. To avoid creating an intermediate structure just for the sake of the HMI, the HMI will interact directly with AxisCommands. 

Similarly, each mapp Framework has an action file called HMIActions.st, which contains all of of the programming related to the HMI interface. 


mapp View Demo Page

A mapp View demo page is included in the mapp Framework so that you can quickly and easily navigate through all the imported contents in Chrome. This page is intended for demonstration purposes only. It is not intended to be used in the final application. 

If you do not yet have a mapp View visualization when you import the Framework, then this Demo page will be assigned as the start page. If you have an existing mapp View application that the Framework merges into, then the Demo page will be added to the pages list and you have to add navigation to this page yourself. 


Access Rights

The following functionality on the mapp View front end is restricted to the following roles:

Framework Component
Feature
Roles that Have Access





Administrators
Service
Operators
Everyone
Audit
Configure the automatic archive export
X




Create an immediate export
X
X


Backup
Restore a backup, change the automatic backup settings
X




Delete a backup
X
X


File
Cut / delete files and configure the FIFO
X
X


Recipe
Create, edit, delete a recipe
X
X



Load a recipe
X
X
X

Report
Delete a report
X
X


UserX
View the user list, edit / add / delete / import / export users
X



Axis
Use the axis faceplate
X
X
X


The default administrative user is 'Admin' with default password '123ABc'. The password must be changed after import. 