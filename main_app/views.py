from bson.objectid import ObjectId
from django import forms
from django.shortcuts import render

from my_blog_website.settings import client

blogs_database = client["Blogs"]
blogs_collection = blogs_database["Blogs"]

class BlogForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField()

# Create your views here.
def index_page(request):
    return render(request, "index.html")

def about_me_page(request):
    return render(request, "about_me.html")

def blogs_page(request):
    projection = {"title": 1, "_id": 1}
    blog_documents = list(blogs_collection.find({}, projection))
    for blog_document in blog_documents:
        blog_document["id_str"] = blog_document["_id"]
    return render(request, "blogs.html", {"blogs": blog_documents})

def blog_page(request, id: str):
    document_id = ObjectId(id)
    if request.method == "POST":
        res = blogs_collection.update_one(
            {"_id": document_id},
            {"$set": {
                "title": request.POST.get("title", ""),
                "content": request.POST.get("content", "")
            }
        })
    blog_document = blogs_collection.find_one({"_id": document_id})
    blog = {"id": blog_document["_id"], "title": blog_document["title"], "content": blog_document["content"]}
    return render(request, "blog.html", {"blog": blog})

def new_blog_page(request):
    if request.method == "POST":
        blog_form = BlogForm(request.POST)
        if blog_form.is_valid():
            title = blog_form.cleaned_data["title"]
            content = blog_form.cleaned_data["content"]
            blogs_collection.insert_one({"title": title, "content": content})
            projection = {"title": 1, "_id": 1}
            blog_documents = list(blogs_collection.find({}, projection))
            for blog_document in blog_documents:
                blog_document["id_str"] = blog_document["_id"]
            return render(request, "blogs.html", {"blogs": blog_documents})
    return render(request, "new_blog.html", {"form": BlogForm()})