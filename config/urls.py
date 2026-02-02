from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="E-commerce Nepal API",
        default_version='v1',
        description="API documentation for E-commerce Nepal",
        terms_of_service="https://www.ecommercenepal.com/terms/",
        contact=openapi.Contact(email="support@ecommercenepal.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),

    # API URLs (will be added as we create apps)
    path('api/v1/auth/', include('apps.users.urls')),
    # path('api/v1/products/', include('apps.products.urls')),
    # path('api/v1/cart/', include('apps.cart.urls')),
    # path('api/v1/orders/', include('apps.orders.urls')),
    # path('api/v1/reviews/', include('apps.reviews.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)

    # Debug toolbar
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
