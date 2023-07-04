import json
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import RequestFactory, TestCase
from django.utils import timezone
