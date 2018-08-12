from django.contrib.gis.db import models
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations
from django.contrib.postgres.fields import JSONField
from django.db import models
import uuid
from django.contrib.gis.db import models
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations

from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, unique=True, blank=True, null=True)
    private_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    public_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    data = JSONField(default={})

    def __str__(self):
        return "%s %s %s %s %s" % (self.public_uuid, self.data.get('identity', {}).get('first_name', ''), self.data.get('identity', {}).get('middle_name', ''), self.data.get('identity', {}).get('last_name', ''), self.data.get('identity', {}).get('birthdate', ''))
