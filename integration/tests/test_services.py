import random
import string

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework.authtoken.models import Token
