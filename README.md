# Cyber Security Base 2022, Project 1

The project is based on a message board web application.  The application can store public messages that can be written and shared by everybody and also private notes, which are not public.  The board shows the titles of the ten most recent public messages, which can be viewed  A user can search for text in public messages and a user can delete his or her private notes.

## Install instructions
- Clone the directory
- Make a virtualenvironment from the requirements.txt
- Start the server with: python manage.py runserver

##### Users already in the system:  
- `admin:samsung111`
- `alice:redqueen`
- `bob:squarepants`

The following vulnerabilities that are found in the code, correspond to the OWASP 2017 list of top ten security risks.

## FLAW 1 Broken access control:
A Broken Access Control violation happen when a user is able to access functions or parts of data that are outside of his or her intended permissions.  Attackers can exploit this to access, add, modify, remove, or do other things with unauthorised data.

The flaw is visible in many parts of the code.  While logged into the site, you can open a message just by clicking a link on the page. The page directs the user to the subdomain http://127.0.0.1:8000/readmessage/<messageid>, where you can read the message. The code does not check that you are the legal owner of the message.  This gives the attacker a possibility to replace the <messageid> part of the url with any number and therefore read other user’s private notes.

How to reproduce:
- Go to http://127.0.0.1:8000
- Login as alice:redqueen
- Add a note if none are present
- Click a raw note data or go to http://127.0.0.1:8000/readnote/0-100
- Change the number at the end of the link and view other users notes
- You can also logout and try to view the url


## Flaw 2 Injection:
The exact source of the flaw is in the deletenote() function at [Line 47](https://github.com/yostiq/mooc-cybersecurity-project-1/blob/c891e3dfc9ff30449589a0a205d1401bda2c1c36/notes/views.py#L47).

The delete function is deleting notes with sql code and inputting the user’s request into the command as a variable. Nothing is done to sanitize the input and therefore it’s possible to easily delete everything from the tables. I’m not very good at sql injection so I’m not sure if you could pull data and see it from the table when the command starts with delete. Maybe something could be done with unions. Also as there are no checks to see if the user deleting the note owns the note, if the attacker knows the contents of another user’s private note they can delete if just like that.

- How to reproduce:
- Go to http://127.0.0.1:8000
- Login as alice:redqueen
- Make sure you have a few notes added
- Try to delete: a' or 1=1 or 1='
- Every note will get deleted.

There are many fixes you could do, I decided to go with django’s model system and just delete the note with commands from that, this way the user’s text variable only gets passed to the django function and django can handle input sanitizing. Another fix I added was to check if the note is actually owned by the user wanting to delete that note.

The fix is in the new deletenote() function at [Line 56](https://github.com/yostiq/mooc-cybersecurity-project-1/blob/86e948124991af5bdd55a5872a9ec45945dc9fd8/notes/views.py#L56).


## FLAW 2 Security misconfiguration:
There are 2 sources for this flaw, the first one is in the python code at [Line 16](https://github.com/yostiq/mooc-cybersecurity-project-1/blob/c891e3dfc9ff30449589a0a205d1401bda2c1c36/notes/views.py#L16).  
The second one is in the html at [Line 24](https://github.com/yostiq/mooc-cybersecurity-project-1/blob/c891e3dfc9ff30449589a0a205d1401bda2c1c36/notes/templates/notes/index.html#L24).

Adding a note does not send a csrf token to the server. The note adding POST form is missing a {% csrf_token %} in the code. Normally this would be ok as when trying to use this form, the server would not send anything and with debugging on, django would complain to add the token. It isn’t ok since the python code linked earlier has @csrf_exempt. This makes it so the server doesn’t require the token.

This flaw is fixed with deleting the @csrf_exempt from the python code and adding {% csrf_token %} into the form in the html.

## FLAW 3 XSS:
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

## Flaw 5 Sensitive data exposure:
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
