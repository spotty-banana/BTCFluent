from django.shortcuts import render
from django.http import HttpResponse
import hashlib

def wallet(request):
    return HttpResponse("You're looking at wallet")
