# Introducion

mapp Technology is the overarching term for the ready-made, modular software products at B&R. This technology enables you to implement complex or tedious features (such as a recipe system) with just a few mapp function blocks and configuration settings rather than creating it from scratch with PLCopen. By using mapp Technology you can complete your application development up to three times faster, with significantly less code than if you wrote it entirely with PLCopen.  

The mapp Framework takes mapp Technology one step further to provide the user with a universal starting point for mapp Technology. This even further reduces the amount of application code that must be written by the application engineer. The Framework includes programming tasks and supporting configuration files with built-in best practices and application know-how. It is designed to be modular, so the user can easily add the specific parts that are relevant to the machine to an existing project. 


Motivation and Goals

The overall goal of the mapp Framework is to streamline and simplify your mapp Services/Axis implementation. More specifically, the goals are:
• Quality
o The Framework is designed with best practices in mind, which have been vetted by several experienced application engineers 
o The goal is to set each mapp user up for success
• Time Savings
o By giving users a reliable starting point, we lower the learning curve of mapp Technology
o New engineers can ramp up faster
o Quicker time to market
• Simplicity
o The mapp Framework is modular without being overly complex
o With a standardized approach to mapp Technology, application support/hand-off and code maintenance become more straightforward  
o The framework is scalable according to the needs of the application 
• Cost savings
o Use of the Framework will result in cost savings for the machine, due to a reduction in the required application engineering time


Community Driven Resource

The mapp Framework is a community driven / open source resource. Input from the community is used to continually refine and improve the mapp Framework. It is not an official product from B&R.

The Github repository which holds the Framework source project is available at the following link: 
https://github.com/br-automation-com/mapp-Framework 
Applications engineers can therefore suggest modifications or new functionality directly via Github. In this way, the mapp Framework is constantly evolving and improving via input from the community. 

The mapp Framework uses standard mapp components, and general questions about mapp should continue to be directed to 1st level / 2nd level support. However, since the Framework itself is a community driven resource, questions about the mapp Framework should be asked within the B&R Community forum. Use the tag "mapp-framework" to ask a question or report a bug. 


YouTube Tutorial Videos

Short tutorial videos for each component of the mapp Framework are available in a dedicated playlist on the B&R YouTube channel. These tutorial videos supplement the written documentation. 


Availability

A mapp Framework is currently available for the following mapp Technologies: 
 
• mapp AlarmX
• mapp Audit
• mapp Axis
• mapp Backup
• mapp File
• mapp PackML
• mapp Recipe
• mapp Report
• mapp UserX

A corresponding HMI is available in mapp View and VC4. 


Framework Contents

Each mapp Framework contains the following:
• Logical View task(s)
• Configuration file(s) 
• Help files

The supporting Help pages are individualized for each mapp Framework. These pages will identify what is included in the framework and any changes that are necessary to properly embed the framework to an existing application. It is important to note that the documentation focuses on the Framework itself, and not the fundamentals of mapp Services / mapp Motion. For details on the fundamentals of mapp Technology, refer to the respective sections in the Help ("Services" → "mapp Services", or "Motion control" → "mapp Motion"). 

IMPORTANT: Every mapp Framework Help section has a page titled "Required Modifications". The steps on this page must be executed in order to get the Framework into a functional state! 


MIT License

Copyright (c) 2022 B&R Industrial Automation

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