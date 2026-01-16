"""
URL configuration for Smart SPC project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'Smart SPC API',
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    path('api/v1/dashboard/', include('dashboard.urls')),
    path('api/v1/qcost/', include('qcost.urls')),
    path('api/v1/inspection/', include('inspection.urls')),
    path('api/v1/spc/', include('spc.urls')),
    path('api/v1/qa/', include('qa.urls')),
    path('api/v1/pm/', include('predictive_maintenance.urls')),

    # New API endpoints
    path('api/v1/quality/', include('quality_issues.urls')),
    path('api/v1/equipment/', include('equipment.urls')),
    path('api/v1/tools/', include('tools.urls')),
    path('api/v1/work-orders/', include('work_orders.urls')),
    path('api/v1/integration/', include('integration.urls')),
]
