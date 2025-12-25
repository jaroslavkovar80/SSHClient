## 🛡️ mapp Audit Framework Features

The following features and functionality are included in the **mapp Audit Framework**:

* **Two audit systems**:

  1.mapp Services events
     - This audit trail captures all built-in events related to the other mapp Services frameworks that are included in the project

  2.Custom events

     - This audit trail can be used for **debugging and troubleshooting** the application
     - The intention is to leave **breadcrumbs** throughout the application to help track down bugs in the application code
     - For example, when troubleshooting a page fault, a custom audit event can be triggered at the top of every task or in several places throughout a task to narrow down where the page fault occurs
     - The text for the custom audit event is provided directly to the **MpAuditCustomEvent()** function  
       For more details, see here

* mapp View content to view the **audit list**
  - The audit systems use **separate display texts**.The text shown on the **HMI** is different from the text exported to the file.This allows a succinct message to be shown on the HMI, with optional timestamp, user, or other context.The exported audit file contains more detailed information directly in the message

* The ability to **export an audit archive** and choose the **export format** via the HMI
* The ability to **configure automatic archiving**
* The **text system** is set up to generate applicable text for all **mapp Services audit events**
* A **query** along with a **supporting state machine** to query large amounts of data

---

### 🧾 Variable Monitoring Audit Example

An example of setting up a **variable monitoring audit event** is provided within the Framework:

* You can choose to record **value change events** of specific variables by adding them to the **Variable Monitor** list in the **mapp Audit Configuration**
  
  * The provided example uses the variable **::AuditMgr:VariableMonitorExample**

* The **localizable text definition** for these events is defined in the **TxtDatapoints.tmx** files
  * Namespace **MpAudit/DP** for the exported text Namespace **MpAudit/Display/DP** for the displayed text
  * The **text ID** must be equal to the fully resolved variable name (**::AuditMgr:VariableMonitorExample** in this case)

---

### 🔐 Access Rights

The ability to **configure automatic archive export** is restricted to the **Administrators** role.

The ability to **create an immediate export** is restricted to the **Administrators** or **Service** role.

The default administrative user is **Admin** with the default password **123ABc**.  
The password **must be changed after import**.