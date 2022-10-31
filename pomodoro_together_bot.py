from telegram.ext import CommandHandler, MessageHandler, JobQueue
from telegram.ext import Job

#APItoken validation
from sys import argv
import TokenValidityCheck
if len(argv)<=1:
    raise TokenValidityCheck.NoAPIKeySpecified(None)

if len(argv)>2:
    raise TokenValidityCheck.TooManyArgs(apikey = None, arg_amount = 1) 

if TokenValidityCheck.CheckForAPIKey(argv[1]):
    APItoken = argv[1]
###
timer_multiplier=60

from telegram.ext import Updater
upd = Updater(token=APItoken, use_context=True)
disp = upd.dispatcher
job = upd.job_queue
import logging
logging.basicConfig(format='>%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

#How args are passed: /command 1 2 3
#/command 1 2 is valid too
# 1 - work session; 2 - short rest; 3 - long rest
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='''How to use this bot:
/schedule <work time> <short rest> <number of sessions; default=1>
Example:
/schedule 25 5
Default pomodoro session with 25 minute work time followed by 5 minute break''')
def schedule(update, context):
    correct_types=all(arg.isdigit() for arg in context.args)
    if not correct_types:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Please make sure you send numbers as a command argument')
        return
    converted_args = [int(arg) for arg in context.args]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Mapping your session')
    if len(converted_args)>=3:
        schedule_plan = schedule_mapper(update, context, int(converted_args[0])*timer_multiplier, int(converted_args[1])*timer_multiplier, int(converted_args[2]))
        return
    schedule_plan = schedule_mapper(update, context, int(converted_args[0])*timer_multiplier, int(converted_args[1])*timer_multiplier)
    return

    #try:
    #    schedule_plan = schedule_mapper(update, context, int(context.args[0])*timer_multiplier, int(context.args[1])*timer_multiplier, int(context.args[2]))
    #except:
    #    schedule_plan = schedule_mapper(update, context, int(context.args[0])*timer_multiplier, int(context.args[1])*timer_multiplier)

def debug_mode(update, context):
    print(update.effective_user.id,": debug mode called")
    print(len(context.args))
    if len(context.args) < 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text='To enter debug mode you need to send api token to prove ownership')
        print(update.effective_user.id,": debug mode token not specified")
        return

    if context.args[0] != APItoken:
        print(update.effective_user.id,": debug mode token failed")
        return

    global timer_multiplier
    if timer_multiplier == 60:
        timer_multiplier = 1
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'''Debug mode enabled, minutes will be treated as seconds
current variables are:
    timer_multiplier={timer_multiplier}
    active jobs:
    {[sesh.name for sesh in job.jobs()]}''')
    elif timer_multiplier == 1:
        timer_multiplier=60
        context.bot.send_message(chat_id=update.effective_chat.id, text='Debug mode disabled, everything is back to normal')

def list_active_sessions(update, context):
    if len(context.args) < 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text='To list active jobs you need to send api token to prove ownership')
        print(update.effective_user.id,": list active jobs token not specified")
        return

    if context.args[0] != APItoken:
        print(update.effective_user.id,": list active jobs token failed")
        return
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'''
active jobs:
{[sesh.name for sesh in job.jobs()]}''')


def schedule_mapper(update, context, work, rest, times=1):
    job.run_once(callback=on_work_timer, when = work, context=(update.effective_chat.id, work, rest, times), name=f'{update.effective_chat.id}:work')
#    job.run_once(callback=on_rest_timer, when = work+rest, context=update.effective_chat.id, name=f'{update.effective_chat.id}:rest')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Your session is successfully launched! Time to work.')

def on_work_timer(context):
    chat_id = context.job.context[0]
    work = context.job.context[1]
    rest = context.job.context[2]
    times = context.job.context[3]
    context.bot.send_message(chat_id = chat_id, text = 'Work session finished, rest session started')
    job.run_once(callback=on_rest_timer, when=rest, context=(chat_id, work, rest, times), name=f'{chat_id}:rest')

def on_rest_timer(context):
    chat_id = context.job.context[0]
    work = context.job.context[1]
    rest = context.job.context[2]
    times = context.job.context[3] - 1
    context.bot.send_message(chat_id = chat_id, text = f'Rest session finished{", work session started"*(times>=1)}{". This is the last pomodoro"*(times<1)}')
    if times>0:
        job.run_once(callback=on_work_timer, when = work, context = (chat_id, work, rest, times), name=f'{chat_id}:work')

def cancel_all_sessions(update, context):
    chat_id = update.effective_chat.id
    worksessions = job.get_jobs_by_name(f'{chat_id}:work')
    restsessions = job.get_jobs_by_name(f'{chat_id}:rest')
    allsessions = worksessions + restsessions
    for sesh in allsessions:
        sesh.schedule_removal()
    context.bot.send_message(chat_id = chat_id, text = "Cancelled all sessions in this chat")


    


schedule_handler = CommandHandler('schedule', schedule)
start_handler = CommandHandler('start', start)
debug_handler = CommandHandler('debug', debug_mode)
list_active_sessions_handler = CommandHandler('listsesh', list_active_sessions)
cancel_all_sessions_handler = CommandHandler('cancel', cancel_all_sessions)
disp.add_handler(start_handler)
disp.add_handler(schedule_handler)
disp.add_handler(debug_handler)
disp.add_handler(list_active_sessions_handler)
disp.add_handler(cancel_all_sessions_handler)
upd.start_polling()
upd.idle()
