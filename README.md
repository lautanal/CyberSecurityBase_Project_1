# Cyber Security Base 2022, Project 1

The project is based on a message board web application.  The application stores public messages that can be written and are shared by everybody. The board shows the titles of the ten most recent messages, which can be viewed by clicking the link.  Besides that a user can store private notes, which are not public.  A user can search for text in the public messages and can delete his or her own private notes.  

## Install instructions
- Clone the directory
- Make a virtualenvironment from the requirements.txt
- Start the server with: python manage.py runserver

##### Users already in the system:  
- `admin:samsung111`
- `alice:redqueen`
- `bob:squarepants`

In the code you can find the following vulnerabilities.  The vulnerabilities are classified according to the OWASP 2017 list of top ten security risks.

## FLAW 1: Broken access control
Location of the flaw: views.py readmessage() function [line 32](https://github.com/lautanal/CyberSecurityBase_Project_1/blob/main/messenger/views.py#L34)

A Broken Access Control violation happens when a user is able to access functions or parts of data that are outside of his or her intended permissions.  Attackers can exploit this to access, add, modify, remove, or do other things with unauthorised data.

The flaw is visible in many parts of the code.  While logged into the site, you can open a message just by clicking a link on the page. The page directs the user to the subdomain http://127.0.0.1:8000/readmessage/<messageid>, where you can read the message. The code does not check that you are the legal owner of the message.  This gives the attacker a possibility to replace the <messageid> part of the url with any number and therefore read other user’s private notes.  You can delete other user's messages in the same fashion.

The flaw can be fixed simply by adding an if statement that checks that the user is the owner of the message:
```
    if request.user == message.sender:
         response = HttpResponse(message.content, content_type="text/plain")
         return response
     else:
         return render(request, "messenger/forbidden.html")
```

## FLAW 2: Injection
Location of the flaw: : views.py searchmessage() function [line 53](https://github.com/lautanal/CyberSecurityBase_Project_1/blob/main/messenger/views.py#L53)

Injection is a vulnerability in the code, where a malicious user can send code to the server hidden as regular user data, which is executed as commands on the server. One of the most common forms of injection is SQL injection where database queries are made without "cleaning" or "sanitizing" user data i.e. making sure it contains only what it is supposed to.

The flaw in my code is in the search message function SQL-query.  The searched text is simply concatenated to the body of the SQL-query.  This gives an attacker a possibility to add malicious code to the search query.  For example with input '-- , the attacker can see all private notes of other users.

The flaw can be fixed by parameterizing all user input.  If the user input is given to the SQL-query as parameters, the values of the user input are added to the SQL command at execution time in a controlled manner.  The SQL engine checks each parameter to ensure that it is correct for its column and are treated literally, and not as part of the SQL to be executed.


## FLAW 3: Cross-Site Request Forgery (CSRF)

Locations of the flaw: views.py addmessage() function [line 17](https://github.com/lautanal/CyberSecurityBase_Project_1/blob/main/messenger/views.py#L17), 
    index.html [line 25](https://github.com/lautanal/CyberSecurityBase_Project_1/blob/main/messenger/templates/messenger/index.html#L25)

Cross-site request forgery is an attack where existing user priviliges of an authenticated user are used to make malicious requests and access private user data. A CSRF attack takes advantage of the fact that applications do not have the capacity to recognize the difference between malicious and secure requests once a user is authenticated. Attackers usually initiate the process by creating a corrupted link that they send to the target via email, text, or chat.

The flaws in my code are in function addmessage() and in index.html file.  Django provides protection for CSRF attacks but it is exempted by a Python decorator.  The index.html file should have {% csrf_token %} added to every form to force the CSRF cookie.
    
To fix these flaws we only need to add {% csrf_token %} to each form in our application and Django will take care of the rest.



## FLAW 4: XSS
Location of the flaw: views.py readmessage() function [line 36](https://github.com/lautanal/CyberSecurityBase_Project_1/blob/main/messenger/views.py#L36).

Adding a note and then viewing the note’s data in the browser will render that note as html. This means you can put javascript between <script> tags to execute whenever any user opens that message.

How to reproduce:
- Go to http://127.0.0.1:8000
- Login as alice:redqueen
- Add a note with <script\>alert(1)</script\> and set to public if you want to test on another account
- Click the note’s raw note data and observe the alert
- Optionally login with another account
- Logout and login with bob:squarepants
- Open the public note’s raw note data
- Observer the alert popping up

The current way the server handles notes can be fixed with a quick hack to render the notes in as plain text. This is shown in the fixed readnote() function at [Line 37](https://github.com/yostiq/mooc-cybersecurity-project-1/blob/c891e3dfc9ff30449589a0a205d1401bda2c1c36/notes/views.py#L37). Instead of setting the content_type of the response to text/html, we set it to text/plain. This will make it so no html is parsed when the page is opened. The better way to fix this would be to actually sanitize the input and not have a dedicated page to see the “raw data” of notes, but as this is an exercise I thought this quick hack would be good.



## FLAW 5: Security Logging and Monitoring Failures

Failures in security logging and monitoring are flaws that lead to inability to detect malicious use. Not only does this mean that responding to these breaches is impossible (since one does not even know they are happening), but the root cause of these breaches remains unearthed. Proper logging and monitoring is essential in making sure that one can act in response to security breaches and fix any vulnerabilities as they give a hint to the developer as to how to correct them.

As there is no logger currently in use in the project, fixing this flaw requires us to simply add a logger to our project and then configure it to log any important actions in our app. We could for example log every time that a poll is created or voted on or the adming logs in to the app etc. 
