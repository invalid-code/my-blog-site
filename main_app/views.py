import logging
import os

from bson.objectid import ObjectId
from django import forms
from django.http import Http404, HttpResponseServerError
from django.shortcuts import redirect, render

from my_blog_website.settings import MEDIA_ROOT, client

logger = logging.getLogger(__name__)

blogs_database = client["Blogs"]
blogs_collection = blogs_database["Blogs"]


class BlogForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField()
    images = forms.FileField()


# Create your views here.
def index_page(request):
    logger.info("/ Requested")
    return render(request, "index.html")


def about_me_page(request):
    logger.info("/about-me Requested")
    return render(request, "about_me.html")


def blogs_page(request):
    logger.info("/blogs Requested")
    projection = {"title": 1, "_id": 1}
    blog_documents = blogs_collection.find({}, projection)
    blogs: list[dict[str, str]] = []
    for blog_document in blog_documents:
        blogs.append(
            {
                "id_str": str(blog_document["_id"]),
                "title": blog_document["title"],
            }
        )
    logger.debug("Getting blogs")
    return render(request, "blogs.html", {"blogs": blogs})


def blog_page(request, id: str):
    document_id = ObjectId(id)
    if request.method == "POST":
        match request.POST.get("action"):
            case "update":
                result = blogs_collection.update_one(
                    {"_id": document_id},
                    {
                        "$set": {
                            "title": request.POST.get("title", ""),
                            "content": request.POST.get("content", ""),
                        }
                    },
                )
                if result.modified_count < 1:
                    logger.error(f"Couldn't update blog with blog id = {id}")
                else:
                    logger.debug(f"Updated blog with blog id = {id}")
                image = request.FILES.get("image")
                if image is not None:
                    image_file_dest = os.path.join(MEDIA_ROOT, id)
                    with open(image_file_dest, "wb+") as f:
                        for chunk in image.chunks():
                            f.write(chunk)
            case "delete":
                result = blogs_collection.delete_one({"_id": document_id})
                if result.deleted_count < 1:
                    logger.error("Couldn't delete blog with blog id = {id}")
                else:
                    logger.debug("Deleted blog with blog id = {id}")
                os.remove(os.path.join(MEDIA_ROOT, id))
                logger.info("Redirecting to /blogs")
                return redirect("blogs")
    blog_document = blogs_collection.find_one({"_id": document_id})
    if blog_document is None:
        logger.error(f"Blog with id = {id} doesn't exists")
        raise Http404(f"Blog with id = {id} doesn't exists")
    logger.info(f"/blogs/{id} Requested")
    blog = {
        "id": blog_document["_id"],
        "title": blog_document["title"],
        "content": blog_document["content"],
    }
    return render(request, "blog.html", {"blog": blog})


def new_blog_page(request):
    if request.method == "POST":
        blog_form = BlogForm(request.POST, request.FILES)
        if blog_form.is_valid():
            title = blog_form.cleaned_data["title"]
            content = blog_form.cleaned_data["content"]
            image = request.FILES["images"]
            result = blogs_collection.insert_one(
                {"title": title, "content": content}
            )
            if result.inserted_id:
                logger.debug("Created a new blog")
            else:
                logger.error("Error creating new blog")
                return HttpResponseServerError(
                    "Error creating new blog".encode("utf-8")
                )
            image_file_dest = os.path.join(MEDIA_ROOT, str(result.inserted_id))
            with open(image_file_dest, "wb+") as f:
                for chunk in image.chunks():
                    f.write(chunk)
            logger.info("Redirecting to /blogs")
            return redirect("blogs")
    else:
        blog_form = BlogForm()
    logger.info("/blogs/new Requested")
    return render(request, "new_blog.html", {"form": blog_form})
