from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_page, name="home"),
    path("about-me", views.about_me_page, name="about_me"),
    path("blogs", views.blogs_page, name="blogs"),
    path("blogs/<str:id>", views.blog_page, name="blog")
]