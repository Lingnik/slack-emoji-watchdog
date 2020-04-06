import os
import json
import redis
import datetime

r = redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.csrf import csrf_exempt


def home(request):

    template = loader.get_template('watchdog_web_service/index.html')
    return HttpResponse(template.render(context, request))


@csrf_exempt
def bot_slash_command(request):
    """Handle Slack /emoji-watchdog commands.
    
    :param request: 
    :return: 
    """
    response_url = str(request.POST.get('response_url'))
    channel_id = str(request.POST.get('channel_id'))
    user_id = str(request.POST.get('user_id'))
    command = str(request.POST.get('text'))
    command = command.strip()

    print(f"<@{user_id}> ran a command in <#{channel_id}>: /emoji-watchdog {command}")

    if command == 'help':
        # /emoji-watchdog help
        template = loader.get_template('watchdog_web_service/bot_slash_help.txt')
        context = {
            'response_url': response_url,
            'user_id': user_id,
            'channel_id': channel_id,
        }
        return HttpResponse(template.render(context, request))
    if command == 'unmute':
        # /emoji-watchdog unmute
        r.delete(f'mute.{user_id}')
        return HttpResponse('Your status will appear in #emoji-watchdog again.')
    if command.startswith('mute '):
        # /emoji-watchdog mute 1h
        hours = command.split(' ')[1]
        hours = hours.strip('h')
        try:
            hours = int(hours)
        except Exception as e:
            return HttpResponse(status=500, content=(
                'I was unable to recognize the number you provided for hours.'
                ' You provided `{command.split(' ')[1]}` which does not match the integer format `8h` or `8`.'
            ))
        timestamp = datetime.datetime.now().timestamp() + (hours * 60.0 * 60.0)
        r.set(f'mute.{user_id}', timestamp)
        return HttpResponse(f'I will hide your activity for {hours} hours.')
    if command == 'list':
        # /emoji-watchdog list
        r.lpush('slash.list', f'{channel_id},{user_id}')
        return HttpResponse(":wave: Hang on a sec, I'll fetch player activities and get back to you.")
    return HttpResponse(
        ("I couldn't understand your command. Try `/emoji-watchdog help`.\n"
         f"Your command: `/emoji-watchdog {command}`"))
