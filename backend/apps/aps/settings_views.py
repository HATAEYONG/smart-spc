from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .settings_models import UserSettings, Preset, UserActivity, SystemConfiguration
from rest_framework import serializers


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = "__all__"
        read_only_fields = ["setting_id", "created_at", "updated_at"]


class PresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preset
        fields = "__all__"
        read_only_fields = ["preset_id", "created_at", "updated_at", "usage_count", "last_used"]


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = "__all__"
        read_only_fields = ["activity_id", "timestamp"]


class SystemConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfiguration
        fields = "__all__"
        read_only_fields = ["config_id", "created_at", "updated_at"]


class UserSettingsViewSet(viewsets.ModelViewSet):
    """
    User settings management
    """
    queryset = UserSettings.objects.all()
    serializer_class = UserSettingsSerializer

    @action(detail=False, methods=["get", "put"])
    def my_settings(self, request):
        """
        GET/PUT /api/aps/user-settings/my_settings/
        Get or update current user's settings
        """
        user_id = request.query_params.get("user_id", "default_user")

        if request.method == "GET":
            settings, created = UserSettings.objects.get_or_create(
                user_id=user_id,
                defaults=self._get_default_settings(user_id)
            )
            return Response(UserSettingsSerializer(settings).data)

        elif request.method == "PUT":
            settings, created = UserSettings.objects.get_or_create(user_id=user_id)

            # Update settings
            for key, value in request.data.items():
                if hasattr(settings, key) and key not in ["setting_id", "user_id", "created_at"]:
                    setattr(settings, key, value)

            settings.save()
            return Response(UserSettingsSerializer(settings).data)

    @action(detail=False, methods=["post"])
    def reset_to_default(self, request):
        """
        POST /api/aps/user-settings/reset_to_default/
        Reset settings to default
        """
        user_id = request.data.get("user_id", "default_user")

        try:
            settings = UserSettings.objects.get(user_id=user_id)
            defaults = self._get_default_settings(user_id)

            for key, value in defaults.items():
                setattr(settings, key, value)

            settings.save()
            return Response(UserSettingsSerializer(settings).data)
        except UserSettings.DoesNotExist:
            return Response(
                {"error": "Settings not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"])
    def export_settings(self, request):
        """
        GET /api/aps/user-settings/export_settings/
        Export settings as JSON
        """
        user_id = request.query_params.get("user_id", "default_user")

        try:
            settings = UserSettings.objects.get(user_id=user_id)
            return Response({
                "format": "JSON",
                "settings": UserSettingsSerializer(settings).data,
                "exported_at": timezone.now().isoformat(),
            })
        except UserSettings.DoesNotExist:
            return Response(
                {"error": "Settings not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def _get_default_settings(self, user_id):
        """Get default settings"""
        return {
            "user_id": user_id,
            "theme": "LIGHT",
            "language": "ko",
            "timezone": "Asia/Seoul",
            "default_dashboard": "enhanced",
            "dashboard_refresh_interval": 30,
            "show_kpi_cards": True,
            "gantt_view_mode": "WEEK",
            "enable_notifications": True,
            "default_algorithm": "GA",
        }


class PresetViewSet(viewsets.ModelViewSet):
    """
    Preset management
    """
    queryset = Preset.objects.all()
    serializer_class = PresetSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter by type
        preset_type = self.request.query_params.get("type")
        if preset_type:
            qs = qs.filter(preset_type=preset_type)

        # Filter by owner
        owner = self.request.query_params.get("owner")
        if owner:
            qs = qs.filter(owner=owner)

        # Include public presets
        include_public = self.request.query_params.get("include_public", "true")
        if include_public.lower() == "true":
            qs = qs.filter(models.Q(is_public=True) | models.Q(owner=owner)) if owner else qs

        return qs

    @action(detail=True, methods=["post"])
    def use(self, request, pk=None):
        """
        POST /api/aps/presets/{id}/use/
        Mark preset as used and update statistics
        """
        preset = self.get_object()
        preset.usage_count += 1
        preset.last_used = timezone.now()
        preset.save()

        return Response({
            "message": f"Preset '{preset.name}' applied",
            "configuration": preset.configuration,
        })

    @action(detail=True, methods=["post"])
    def toggle_favorite(self, request, pk=None):
        """
        POST /api/aps/presets/{id}/toggle_favorite/
        Toggle favorite status
        """
        preset = self.get_object()
        preset.is_favorite = not preset.is_favorite
        preset.save()

        return Response({
            "message": "Favorite status updated",
            "is_favorite": preset.is_favorite,
        })

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        """
        POST /api/aps/presets/{id}/duplicate/
        Duplicate a preset
        """
        original = self.get_object()

        duplicate = Preset.objects.create(
            name=f"{original.name} (Copy)",
            description=original.description,
            preset_type=original.preset_type,
            configuration=original.configuration.copy() if original.configuration else {},
            owner=request.data.get("owner", original.owner),
            created_by=request.data.get("created_by", "system"),
        )

        return Response(
            PresetSerializer(duplicate).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["get"])
    def system_presets(self, request):
        """
        GET /api/aps/presets/system_presets/
        Get system-provided presets
        """
        preset_type = request.query_params.get("type", "ALGORITHM")

        if preset_type == "ALGORITHM":
            presets = [
                {
                    "name": "Quick Schedule (FIFO)",
                    "preset_type": "ALGORITHM",
                    "description": "Fast scheduling using FIFO rule",
                    "configuration": {
                        "algorithm": "FIFO",
                        "priority": "arrival_time",
                    },
                    "is_system": True,
                },
                {
                    "name": "Quality Focused (GA)",
                    "preset_type": "ALGORITHM",
                    "description": "High-quality schedule using genetic algorithm",
                    "configuration": {
                        "algorithm": "GA",
                        "population_size": 100,
                        "generations": 200,
                        "mutation_rate": 0.05,
                        "objective": "minimize_makespan",
                    },
                    "is_system": True,
                },
                {
                    "name": "Balanced (GA - Fast)",
                    "preset_type": "ALGORITHM",
                    "description": "Balanced performance and quality",
                    "configuration": {
                        "algorithm": "GA",
                        "population_size": 50,
                        "generations": 100,
                        "mutation_rate": 0.1,
                        "objective": "multi_objective",
                    },
                    "is_system": True,
                },
            ]
        elif preset_type == "FILTER":
            presets = [
                {
                    "name": "Today's Jobs",
                    "preset_type": "FILTER",
                    "description": "Show jobs scheduled for today",
                    "configuration": {
                        "date_range": "today",
                        "status": ["PENDING", "RUNNING"],
                    },
                    "is_system": True,
                },
                {
                    "name": "Delayed Jobs",
                    "preset_type": "FILTER",
                    "description": "Show jobs that are behind schedule",
                    "configuration": {
                        "status": "DELAYED",
                        "sort_by": "delay_duration",
                    },
                    "is_system": True,
                },
            ]
        else:
            presets = []

        return Response(presets)

    @action(detail=False, methods=["get"])
    def favorites(self, request):
        """
        GET /api/aps/presets/favorites/
        Get favorite presets
        """
        owner = request.query_params.get("owner")
        favorites = Preset.objects.filter(is_favorite=True)

        if owner:
            favorites = favorites.filter(owner=owner)

        return Response(PresetSerializer(favorites, many=True).data)


class UserActivityViewSet(viewsets.ModelViewSet):
    """
    User activity tracking
    """
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter by user
        user_id = self.request.query_params.get("user_id")
        if user_id:
            qs = qs.filter(user_id=user_id)

        # Filter by activity type
        activity_type = self.request.query_params.get("activity_type")
        if activity_type:
            qs = qs.filter(activity_type=activity_type)

        return qs[:100]  # Limit to recent 100

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        GET /api/aps/user-activity/summary/
        Get activity summary
        """
        user_id = request.query_params.get("user_id")

        activities = UserActivity.objects.all()
        if user_id:
            activities = activities.filter(user_id=user_id)

        # Count by type
        by_type = {}
        for activity_type, _ in UserActivity.ACTIVITY_TYPES:
            by_type[activity_type] = activities.filter(activity_type=activity_type).count()

        # Recent activities
        recent = activities.order_by("-timestamp")[:10]

        return Response({
            "total_activities": activities.count(),
            "by_type": by_type,
            "recent": UserActivitySerializer(recent, many=True).data,
        })


class SystemConfigurationViewSet(viewsets.ModelViewSet):
    """
    System configuration management
    """
    queryset = SystemConfiguration.objects.all()
    serializer_class = SystemConfigurationSerializer

    @action(detail=False, methods=["get"])
    def all_configs(self, request):
        """
        GET /api/aps/system-config/all_configs/
        Get all configurations grouped by category
        """
        configs = SystemConfiguration.objects.all()

        # Group by category
        grouped = {}
        for config in configs:
            category = config.category or "General"
            if category not in grouped:
                grouped[category] = []

            grouped[category].append({
                "key": config.key,
                "value": config.value,
                "value_type": config.value_type,
                "description": config.description,
                "is_editable": config.is_editable,
            })

        return Response(grouped)

    @action(detail=False, methods=["post"])
    def bulk_update(self, request):
        """
        POST /api/aps/system-config/bulk_update/
        Update multiple configurations at once
        """
        configs = request.data.get("configs", [])
        updated = []

        for config_data in configs:
            key = config_data.get("key")
            value = config_data.get("value")

            try:
                config = SystemConfiguration.objects.get(key=key)
                if config.is_editable:
                    config.value = value
                    config.updated_by = request.data.get("updated_by", "system")
                    config.save()
                    updated.append(key)
            except SystemConfiguration.DoesNotExist:
                pass

        return Response({
            "message": f"Updated {len(updated)} configurations",
            "updated_keys": updated,
        })
