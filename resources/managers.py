from django.db import models

class ResourceQuerySet(models.QuerySet):
    def by_user(self, user):
        return self.filter(user=user)

    def resource_id(self, pk):
        return self.filter(pk=pk)

    def user_resource(self, user_id, pk):
        return self.get(user_id=user_id, pk=pk)


class ResourceManager(models.Manager):
    def get_queryset(self):
        return ResourceQuerySet(self.model, using=self._db)

    def by_user_id(self, user_id):
        return self.get_queryset().by_user(user_id)

    def by_resource_id(self, pk):
        return self.get_queryset().resource_id(pk)

    def by_user_resource(self, user_id, pk):
        return self.get_queryset().user_resource(user_id, pk)


