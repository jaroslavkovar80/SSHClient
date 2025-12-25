## Alarm Reactions

The Framework establishes three alarm reactions by default within the alarm mapping.

1. Info (severity 1–9)
2. Warning (severity 10–19)
3. Error (severity 20–29)

![alarm1][def]

The MpAlarmXCheckReaction function is called for each reaction within the AlarmMgr task.

![alarm2][def2]
---

## Optional Modifications

The following optional changes should be considered to align the Framework with the application requirements.

- Adjust the severity ranges  
  - This is done in the AlarmXCfg.mpalarmxcore configuration file

- Rename the reactions  
  - This is done in the AlarmXCfg.mpalarmxcore configuration file  
  - If you do this, remember to change the name in the MpAlarmXCheckReaction function calls in AlarmMgr.st, starting at line 68  
  - Examples of alternative reaction names:
    - SlowDownConveyor
    - HydraulicMotorOff
    - StopAllMotion
    - YellowLamp

- Add or remove reactions  
  - This is done in the AlarmXCfg.mpalarmxcore configuration file  
  - If you do this, remember to add or remove calls to MpAlarmXCheckReaction in AlarmMgr.st accordingly, starting at line 68

- Check for reactions elsewhere in the code  
  - The MpAlarmXCheckReaction function is typically called from other tasks within the application  
  - For example, the axis control task may check for the Error reaction to determine whether a stop command should be sent to the axes  
  - Copy and reuse the IF statements containing MpAlarmXCheckReaction from AlarmMgr.st as needed throughout the application

[def]: images/userpartion1.png
[def2]: images/userpartion1.png

