from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Message
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import sqlite3

@login_required
def index(request):
    public_messages = Message.objects.filter(private = False).order_by("-pub_date")[:10]
    private_messages = Message.objects.filter(sender_id=request.user.id).filter(private = True).order_by("pub_date")
    return render(request, "messenger/index.html", { "private_messages" : private_messages, "public_messages" : public_messages })

# Add message, this path can reveal sensitive data
@login_required
def addmessage(request):
    message = Message()
    message.title = request.GET["title"]
    message.content = request.GET["content"]
    message.pub_date = timezone.now()
    message.sender = request.user
    try:
        if request.GET["public"] == "on":
            message.private = False
    except:
        message.private = True
    message.save()
    return redirect("/")

# Read message, this path is prone to broken access control attack
@login_required
def readmessage(request, noteid):
     message = Message.objects.get(pk=noteid)
     response = HttpResponse(message.content, content_type="text/html")
     return response


# Delete message, this path is prone to broken access control attack
@login_required
def deletemessage(request, noteid):
    Message.objects.get(pk=noteid).delete()
    return redirect("/")

# This path is prone to SQL injection
@csrf_exempt
@login_required
def searchmessage(request):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    text_to_search = request.POST["searchtext"]
    try:
        result = cursor.execute("SELECT * FROM messenger_message WHERE content LIKE '%" + text_to_search + "%' AND private=false;")
        messages = result.fetchall()
        print("FOUND: ", messages)
        return render(request, "messenger/search.html", { "searchtext" : text_to_search, "messages" : messages })
    except:
        return redirect("/")

## Flaw 4 fixed with this function
# @login_required
# def deletemessage(request):
#     message_to_delete = request.POST["content"]
#     Message.objects.filter(content = message_to_delete, sender = request.user).delete()
#     return redirect("/")
