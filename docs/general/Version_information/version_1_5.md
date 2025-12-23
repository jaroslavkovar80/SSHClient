Framework
Description
mapp Audit
• Improved the usability of the audit configuration dialog box
mapp Axis / Cockpit
• The AxisMgr template task is now not added to the software configuration, as opposed to before where it was automatically added but disabled. 
mapp File
• Improved the usability of the FIFO dialog box 
mapp Recipe
• General reorganization and optimization to make the recipe system more robust and easier to extend
Import Tool
• Import the file device definitions depending on the AR version, in order to allow AR versions less than A4.91. For AR <A4.91, the file devices use F:\. For AR >=A4.91, the file devices use USER_PATH. 
• Updated the import tool to allow mixing mapp versions starting with version 5.24 and beyond
• Improved the error message if the import fails due to a previous git reset command
• The import tool will now detect existing .vis files within sub-packages of the mapp View package, as opposed to only .vis files in the root directory
Misc
• Updated to the new mapp Framework logo
