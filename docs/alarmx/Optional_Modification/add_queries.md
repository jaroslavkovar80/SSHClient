## Adding Additional Queries

The ExecuteQuery.st action file contains the programming required to execute the query that comes with the Framework, the ActivateAlarms query.

It also contains the supporting state machine that is used to query large amounts of data.

If you want to add an additional query, the following steps are required.

### Step 1: AlarmMgr.var

1. Copy and paste the variable declaration for QueryActiveAlarms and give it a unique name.  
   Each query requires a dedicated function block instance.

2. Copy and paste the variable declaration for AlarmQuery and give it a unique name.

---

### Step 2: AlarmXCfg.mpalarmxcore

1. Define the new query in the Data Queries section at the bottom of the configuration file.  
   Give the query a unique name.

2. Use the new query variable created in step 1.2 for the process variable connections and the update count.

---

### Step 3: ExecuteQuery.st

1. Copy and paste lines 3–47 of ExecuteQuery.st to duplicate the query handling logic.

2. In the copied code, make the following changes:
   - Replace every instance of QueryActiveAlarms with the new function block name created in step 1.1.
   - Replace the query name assignment with the name of the new query created in step 2.1.
   - Replace every instance of AlarmQuery with the new variable name created in step 1.2.

3. If the new query should run only based on a button press:
   - Add a new boolean command within HmiAlarmX.Commands
   - Update the I


