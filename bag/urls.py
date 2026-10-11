from django.urls import path

from . import views

app_name = "bag"

urlpatterns = [
    path("", views.bag_detail, name="detail"),
    path("add/<int:product_id>/", views.bag_add, name="add"),
    path("update/<str:key>/", views.bag_update, name="update"),
    path("remove/<str:key>/", views.bag_remove, name="remove"),
]
