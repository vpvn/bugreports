from django.db.models import F

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response

from . import models
from . import serializers


class ViewSetActionPermissionMixin:
    def get_permissions(self):
        """Return the permission classes based on action.

        Look for permission classes in a dict mapping action to
        permission classes array, ie.:

        class MyViewSet(ViewSetActionPermissionMixin, ViewSet):
            ...
            permission_classes = [permissions.AllowAny]
            permission_action_classes = {
                'list': [permissions.IsAuthenticated]
                'create': [permissions.IsAdminUser]
                'my_action': [permissions.MyCustomPermission]
            }

            @action(...)
            def my_action:
                ...

        If there is no action in the dict mapping, then the default
        permission_classes is returned. If a custom action has its
        permission_classes defined in the action decorator, then that
        supercedes the value defined in the dict mapping.
        """
        try:
            return [
                permission()
                for permission in self.permission_action_classes[self.action]
            ]
        except KeyError:
            if self.action:
                action_func = getattr(self, self.action, {})
                action_func_kwargs = getattr(action_func, "kwargs", {})
                permission_classes = action_func_kwargs.get(
                    "permission_classes"
                )
            else:
                permission_classes = None

            return [
                permission()
                for permission in (
                    permission_classes or self.permission_classes
                )
            ]


class BuggyProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser, ]
    queryset = models.BuggyProject.objects.all()
    serializer_class = serializers.BuggyProjectSerializer


class BugViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser, ]
    queryset = models.Bug.objects.all()
    serializer_class = serializers.BugSerializer
    filterset_fields = ['project', ]


class OccasionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser, ]
    queryset = models.Occasion.objects.all()
    serializer_class = serializers.OccasionSerializer
    filterset_fields = ['os', 'bug__project', ]

    def perform_create(self, serializer):
        serializer.save(ip=self.request.META['REMOTE_ADDR'])


class ReportsViewSet(ViewSetActionPermissionMixin, mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    '''List of reports or create one.
    '''

    permission_classes = [permissions.AllowAny]
    permission_action_classes = {
        'list': [permissions.IsAuthenticated],
        'create': [permissions.AllowAny],
    }
    queryset = models.BuggyProject.objects.all().values(
        project_id=F('pk'),
        exception_text=F('bugs__exception_text'),
        email=F('bugs__occasions__email'),
        ip=F('bugs__occasions__ip'),
        os=F('bugs__occasions__os'),
        details=F('bugs__occasions__details'),
    )
    serializer_class = serializers.ReportSerializer

    def create(self, request):
        data = {}
        data.update(request.data)
        data.update({'ip': request.META['REMOTE_ADDR']})
        serializer = serializers.ReportSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
