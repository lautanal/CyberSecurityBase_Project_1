# Cyber Security Base 2022, Project 1

The project is based on a message board web application.  The application stores public messages that can be written and are shared by everybody. The board shows the titles of the ten most recent messages, which can be viewed by clicking the link.  Besides that the application can store private notes, which are not public.  A user can search for text in the public messages and can delete his or her private notes.  

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

The flaw in my code is in the searchmessage-function SQL-query.  The searched text is simply concatenated to the body of the SQL-query.  This gives an attacker a possibility to add malicious code to the search query.  For example with input '-- , the attacker can see all private notes of other users.

The flaw can be fixed by parameterizing all user input.  If the user input is given to the SQL-query as parameters, the values of the user input are added to the SQL command at execution time in a controlled manner.  The SQL engine checks each parameter to ensure that it is correct for its column and are treated literally, and not as part of the SQL to be executed.


## FLAW 3: Cross-Site Request Forgery (CSRF)

Locations of the flaw: views.py addmessage() function [line 16](https://github.com/yostiq/mooc-cybersecurity-project-1/blob/c891e3dfc9ff30449589a0a205d1401bda2c1c36/notes/views.py#L17), 
    index.html [line 25](https://github.com/lautanal/CyberSecurityBase_Project_1/blob/main/messenger/templates/messenger/index.html#L25)

Cross-site request forgery is an attack where existing user priviliges of an authenticated user are used to make malicious requests and access private user data. A CSRF attack takes advantage of the fact that applications do not have the capacity to recognize the difference between malicious and secure requests once a user is authenticated. Attackers usually initiate the process by creating a corrupted link that they send to the target via email, text, or chat.

The 
    
    In other words, if a user is logged into, for example, their banks website, a malicious agent can send an unsolicited email or plant an exploit on a site they know the target is going to visit. If the website is vulnerable to CSRF, the attacker can implant a malicious url in an HTML image or link, or if the target website only accepts POST requests, then through an HTML form and some javascript. Once executed it looks like the target has willfully transferred funds to the attacker with no way to remedy the situation other than contacting the bank itself and trying to seek help through them.

To fix these flaws we only need to add {% csrf_token %} to each form in our application and Django will take care of the rest.


## FLAW 3: Security misconfiguration
There are 2 sources for this flaw, the first one is in the python code at [Line 16](https://github.com/yostiq/mooc-cybersecurity-project-1/blob/c891e3dfc9ff30449589a0a205d1401bda2c1c36/notes/views.py#L16).  
The second one is in the html at [Line 24](https://github.com/yostiq/mooc-cybersecurity-project-1/blob/c891e3dfc9ff30449589a0a205d1401bda2c1c36/notes/templates/notes/index.html#L24).

Adding a note does not send a csrf token to the server. The note adding POST form is missing a {% csrf_token %} in the code. Normally this would be ok as when trying to use this form, the server would not send anything and with debugging on, django would complain to add the token. It isn’t ok since the python code linked earlier has @csrf_exempt. This makes it so the server doesn’t require the token.

This flaw is fixed with deleting the @csrf_exempt from the python code and adding {% csrf_token %} into the form in the html.



## FLAW 4: Sensitive data exposure
The exact source of the flaw is in the readnote() function at [Line 32](https://github.com/yostiq/mooc-cybersecurity-project-1/blob/467d089caf8d85a0ff50f965c3ed9de54ce91556/notes/views.py#L32).

Just as we saw earlier, it is easy to read anyone’s notes. Currently the attacker doesn’t even have to be logged in to read any notes. You can either know the exact id of the note or you can bruteforce the id at http://127.0.0.1/readnote/<id\>. The server follows a very simple pattern of starting the note id’s at 0 and incrementing by 1 for all new notes.

- How to reproduce:
- Go to http://127.0.0.1:8000
- Login with alice:redqueen
- Add some notes (this part is just to make sure some notes are in the database)
- Open http://127.0.0.1:8000/readnote/<id>
- Try out a few numbers at the end of the url

If you want to check the id of the notes you can open the db.sqlite3 file in the root directory with any kind of sql explorer program. (sqlite3 for linux terminal or DB browser for sqlite3 for windows)

I made 2 fixes to this problem. The first one is to make sure that a user is even logged in. Currently there are no ways to make new accounts so making sure a user is logged in already lessens the attack surface. The fix is to add @login_required to the readnote() function.

The second fix is to check the user logged in every time /readnote is accessed, this way we can see from the request that the owner of the note is currently logged in. This is fixed by checking the user in the readnote() function.

Both of these are fixed in the commented readnote() function at [Line 37](https://github.com/yostiq/mooc-cybersecurity-project-1/blob/86e948124991af5bdd55a5872a9ec45945dc9fd8/notes/views.py#L37).

## FLAW 5: XSS
The exact source of the flaw is in the readnote() function at [Line 34](https://github.com/yostiq/mooc-cybersecurity-project-1/blob/c891e3dfc9ff30449589a0a205d1401bda2c1c36/notes/views.py#L34).

Adding a note and then viewing the note’s data in the browser will render that note as html. This means you can put javascript between <script\> tags to execute whenever any user opens the url corresponding to that note.

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



## FLAW 6: [Security Logging and Monitoring Failures](https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/)  

Locations of flaws:
https://github.com/oskari83/CyberSecurityBaseProject/blob/master/cybersecurityproject/cybersecurityproject/settings.py#L128
https://github.com/oskari83/CyberSecurityBaseProject/blob/master/cybersecurityproject/polls/views.py#L8

Failures in security logging and monitoring are flaws that lead to inability to detect breaches or malicious use. Not only does this mean that responding to these breaches is impossible (since one does not even know they are happening), but the root cause of these breaches remains unearthed. Proper logging and monitoring is essential in making sure that one can act in response to security breaches and fix any vulnerabilities as they give a hint to the developer as to how to correct them.

As there is no logger currently in use in the project, fixing this flaw requires us to simply add a logger to our project and then configure it to log any important actions in our app. We could for example log every time that a poll is created or voted on or the adming logs in to the app etc. 
