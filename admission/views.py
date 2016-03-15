from django.shortcuts import render
from django.contrib.auth.models import User
from admission.forms import NewAccountForm, AccountForm
from admission.utils import send_mail
from random import randint
from admission import models as mdl
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def home(request):
    form_new = NewAccountForm()
    form = AccountForm()
    number1 = randint(1, 20)
    number2 = randint(1, 20)
    number3 = randint(1, 20)
    sum = number1 + number2
    while number3 > sum:
        number3 = randint(1, 20)
    return render(request, "home.html", {'number1':  number1,
                                         'number2':  number2,
                                         'number3':  number3,
                                         'form_new': form_new,
                                         'form':     form})


def home_error(request, message):
    form_new = NewAccountForm()
    form = AccountForm()
    number1 = randint(1, 20)
    number2 = randint(1, 20)
    number3 = randint(1, 20)
    sum = number1 + number2
    while number3 > sum:
        number3 = randint(1, 20)
    return render(request, "home.html", {'number1':  number1,
                                         'number2':  number2,
                                         'number3':  number3,
                                         'form_new': form_new,
                                         'form':     form,
                                         'message': message})


def new_user(request):
    print('new_user')
    """
    To create a new user for the admission
    :param request:
    :return:
    """
    form_new = NewAccountForm(data=request.POST)
    number1 = request.POST['number1']
    number2 = request.POST['number2']
    number3 = request.POST['number3']

    validation = True
    if form_new.is_valid():
        try:
            result = int(number1) + int(number2) - int(number3)
        except:
            result = None

        if str(result) != form_new['verification'].value():
            validation = False
            form_new.errors['verification'] = "Résultat du calcul incorrect"
    else:
        validation = False
    email = form_new['email_new'].value()

    user = User.objects.filter(email=email)
    if user:
        form_new.errors['email_new_confirm'] = "Il existe déjà un compte pour cette adresse email"
        validation = False

    if validation:
        user = User.objects.create_user(form_new['email_new'].value(),
                                        form_new['email_new'].value(),
                                        form_new['password_new'].value())
        user.is_staff = False
        user.is_superuser = False
        user.is_active = False
        user.first_name = form_new['first_name_new'].value()
        user.last_name = form_new['last_name_new'].value()
        user.save()
        person = mdl.person.Person()
        person.user=user
        person.save()
        # send an activation email
        send_mail.send_mail_activation(request, str(person.activation_code), form_new['email_new'].value())
        # return render(request, "confirm_account.html", {'user_id': user.id})

        #return HttpResponseRedirect('/admission/confirm_account.html')
        #return HttpResponseRedirect('../../../confirm_account.html')
        user_id = user.id
        return HttpResponseRedirect(reverse('account_confirm',  args=(user_id,)))
        #return HttpResponseRedirect('account-confirm')

    else:
        number1 = randint(1, 20)
        number2 = randint(1, 20)
        number3 = randint(1, 20)
        sum = number1 + number2
        while number3 > sum:
            number3 = randint(1, 20)
        return render(request, "home.html", {'number1': number1,
                                             'number2': number2,
                                             'number3': number3,
                                             'form_new': form_new})


def activation_mail(request, user_id):
    """
    To re-send an activation email
    :param request:
    :param user_id:
    :return:
    """
    if request.method == "POST":
        user = User.objects.get(pk=user_id)
        person = mdl.person.find_by_user(user)
        if person:
            send_mail.send_mail_activation(request, str(person.activation_code), user.email)
            return HttpResponseRedirect(reverse('admission'))
        else:
            return HttpResponseRedirect(reverse('admission'))
    return HttpResponseRedirect(reverse('admission'))


def activation(request, activation_code):
    person = mdl.person.find_by_activation_code(activation_code)
    if person:
        user = User.objects.get(pk=person.user.id)
        if person and user:
            user.is_active = True
            user.save()
            # to avoid a double activation
            person.activation_code = None
            person.save()
            return render(request, "confirmed_account.html", {'user': user})
        else:
            return render(request, "activation_failed.html")
    else:
        return render(request, "activation_failed.html")


def connexion(request):
    form = AccountForm(data=request.POST)

    user = authenticate(username=form['email'].value(), password=form['password'].value())

    if user is not None:
        # the password verified for the user
        if user.is_active:
            message = "User is valid, active and authenticated"
            return render(request, "admission.html", {'user': user})
        else:
            message = "The password is valid, but the account has been disabled!"
            return home_error(request, message)
    else:
        # the authentication system was unable to verify the username and password
        message = "The username and password were incorrect."
        return home_error(request, message)


def account_confirm(request,user_id):
     return render(request, "confirm_account.html",{'user':user_id})