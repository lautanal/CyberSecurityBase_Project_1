# Cyber Security Base 2022, Project 1

The project is based on a message board web application.  The application stores public messages that can be written and read by everybody. The message board shows the titles of the ten most recent messages, which can be viewed by clicking the title link.  Besides that a user can store private notes, which are not public.  A user can search for a text string in the public messages and can delete his or her own private notes.  

## Link to Repository
https://github.com/lautanal/CyberSecurityBase_Project_1

## Install instructions
- Clone the directory
- Make a virtual environment from requirements.txt
- Start the server with: python manage.py runserver

##### Users already in the system:  
- `admin:admin`
- `anna:annansalasana`
- `janne:jannensalasana`
- `lasse:lassensalasana`

In the code you can find the following vulnerabilities.  The vulnerabilities are classified according to the OWASP 2017 list of top ten security risks.

## FLAW 1: Broken access control
Location of the flaw: `views.py readmessage()` function [line 38](https://github.com/lautanal/CyberSecurityBase_Project_1/blob/main/messenger/views.py#L38)

A Broken Access Control violation happens when a user is able to access functions or parts of data that are outside of his or her intended permissions.  Attackers can exploit this to access, add, modify, remove, or do other things with unauthorised data.

The flaw is visible in many parts of the code.  While logged into the site, you can open a message just by clicking a link on the page. The page directs the user to the subdomain `http://127.0.0.1:8000/readmessage/<messageid>` where you can read the message. The code does not check that you are the legal owner of the message.  This gives the attacker a possibility to replace the `<messageid>` part of the url with any number and therefore read other user’s private notes.  You can delete other user's messages in the same fashion.

The flaw can be fixed simply by adding an if statement that checks that the user is the owner of the message:
```
    if request.user == message.sender:
         response = HttpResponse(message.content, content_type="text/plain")
         return response
     else:
         return render(request, "messenger/forbidden.html")
```

## FLAW 2: Injection
Location of the flaw: : `views.py searchmessage()` function [line 58](https://github.com/lautanal/CyberSecurityBase_Project_1/blob/main/messenger/views.py#L58)

Injection is a vulnerability in the code where a malicious user can send code to the server hidden as regular user data, which is executed as commands on the server. One of the most common forms of injection is SQL injection, where database queries are made without "sanitizing" user data i.e. making sure it contains only what it is supposed to do.

The flaw in my code is in the search message function SQL-query.  The searched text is simply concatenated to the body of the SQL-query.  This gives an attacker a possibility to add malicious code to the search query.  For example with input `'--` the attacker can see all private notes of other users.

The flaw can be fixed by parameterizing all user input.  If the user input is given to the SQL-query as parameters, the values of the user input are added to the SQL command at execution time in a controlled manner.  The SQL engine checks each parameter to ensure that it is correct for its column and are treated literally, and not as part of the SQL to be executed.


## FLAW 3: Cross-Site Request Forgery (CSRF)

Locations of the flaw: `views.py addmessage()` function [line 19](https://github.com/lautanal/CyberSecurityBase_Project_1/blob/main/messenger/views.py#L19), 
    `index.html` [line 25](https://github.com/lautanal/CyberSecurityBase_Project_1/blob/main/messenger/templates/messenger/index.html#L25)

Cross-site request forgery is an attack where existing user priviliges of an authenticated user are used to make malicious requests and access private user data. A CSRF attack takes advantage of the fact that applications do not have the capacity to recognize the difference between malicious and secure requests once a user is authenticated. Attackers usually initiate the process by creating a corrupted link that they send to the target via email, text, or chat.

The flaws in my code are in the `addmessage()` function and in the `index.html` file.  Django provides protection against CSRF attacks, but in my code protection is exempted by a Python decorator.  The `index.html` file is also missing the tag `{% csrf_token %}` which forces the CSRF token to be sent.
    
To fix these flaws we only need to add the`{% csrf_token %}`tag to each form in our application and Django will take care of the rest.



## FLAW 4: Cross-Site Scripting (XSS)
Location of the flaw: `views.py readmessage()` function [line 39](https://github.com/lautanal/CyberSecurityBase_Project_1/blob/main/messenger/views.py#L39).

The present application renders messages as `html` in the `readmessage()` function. This means that Javascript code can be put between `<script>` tags in the message and will be executed anytime a user opens the message.

The flaw can be easily fixed with a change to render the messages as plain text. This is shown in the commented `readnote()` function at [line 40](https://github.com/lautanal/CyberSecurityBase_Project_1/blob/main/messenger/views.py#L40). Instead of setting the content type of the response to `text/html`, we set it to `text/plain`. This will prevent html parsing and Javascript execution when the message is opened. A better way to fix this issue would be to actually sanitize the input and to have a dedicated html page to view the message.



## FLAW 5: Insufficient Logging & Monitoring

Failures in security logging and monitoring are flaws that lead to inability to detect malicious use of system. Without monitoring responding to breaches is impossible since one does not even know what is happening. Proper logging and monitoring are essential in making sure that one can react to security breaches and fix any vulnerabilities immediately.

There is no logger currently in use in the project.  There is no way to detect attackers that are using the vulnerabilities of the code for malicious requests.

Fixing this issue requires proper monitoring to be set up.  We can simply add a logger to our project and configure it to log important actions in the app. We could for example log every time that a message is created or the admin logs etc. The monitoring function can be achieved with proper middleware as well.  
