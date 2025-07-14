from bson.objectid import ObjectId
from django.shortcuts import render

from my_blog_website.settings import client

blogs_database = client["Blogs"]
blogs_collection = blogs_database["Blogs"]


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
    blog = blogs_collection.find({"_id": document_id})
    return render(request, "blog.html", {"blog": blog})