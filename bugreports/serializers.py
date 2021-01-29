'''
DRF bugreports serializers
=================

'''

from rest_framework import serializers
from . import models


class BuggyProjectSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='bugreports:buggyproject-detail')

    class Meta:
        model = models.BuggyProject
        fields = [
            'id',
            'name',
            'url',
        ]


class BugSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='bugreports:bug-detail')

    project = serializers.PrimaryKeyRelatedField(
        queryset=models.BuggyProject.objects.all()
    )

    class Meta:
        model = models.Bug
        fields = [
            'url', 'ts_add', 'project', 'buguuid',
            'exception_text',
            'description', 'discussian_url',
        ]


class OccasionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='bugreports:occasion-detail')

    bug = serializers.PrimaryKeyRelatedField(queryset=models.Bug.objects.all())

    class Meta:
        model = models.Occasion
        fields = [
            'url', 'ts_add', 'bug', 'email', 'ip',
            'os', 'details',
        ]


class ReportSerializer(serializers.Serializer):
    '''Serializer for reports.'''

    project_id = serializers.CharField(required=True, allow_blank=False,
                                       max_length=20)
    exception_text = serializers.CharField(required=True, allow_blank=False)
    email = serializers.EmailField(required=False, allow_null=True)
    ip = serializers.IPAddressField(required=False, allow_null=True)
    os = serializers.ChoiceField(
        required=False, choices=models.OS_CHOICES, allow_null=True)
    details = serializers.CharField(required=False, allow_null=True)

    def create(self, validated_data):
        '''Create and return a new `Occasian` instance.

        Bug with identical exception_text creates only once per project
        '''

        try:
            prj = models.BuggyProject.objects.get(
                pk=validated_data.get('project_id')
            )
        except models.BuggyProject.DoesNotExist:
            raise serializers.ValidationError(
                f"Can't find project with id "
                f"'{validated_data.get('project_id')}'"
            )

        bug, created = models.Bug.objects.get_or_create(
            buguuid=models.buguuid(
                validated_data.get('project_id'),
                validated_data.get('exception_text'),
                                   ),
            defaults={
                'project': prj,
                'exception_text': validated_data.get('exception_text'),
            }
        )

        occasion = models.Occasion.objects.create(
            bug=bug,
            email=validated_data.get('email'),
            ip=validated_data.get('ip'),
            os=validated_data.get('os'),
            details=validated_data.get('details'),
        )

        item = {
            'project_id': occasion.bug.project.pk,
            'exception_text': occasion.bug.exception_text,
            'email': occasion.email,
            'ip': occasion.ip,
            'os': occasion.os,
            'details': occasion.details,
        }

        return item
