import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import AccountProjectModel, AccountModel, AccountPermissionsModel, AccountDevicesModel
from .forms import CreateProjectForm, EditAdminForm, NewAdminUserForm, CreateDeviceForm
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404


def check_own_project(request, project_id):
    user = request.user
    current_account = AccountModel.users.get(user=user)
    prj_id = get_object_or_404(AccountProjectModel, id=project_id)
    if len(prj_id.permissions.filter(account=current_account)) == 0:
        return False
    return True


@login_required
def account(request):
    user = request.user
    account = AccountModel.users.get(user=user)
    list_projects = AccountProjectModel.projects.filter(users=account)
    if request.method == 'POST':
        form = CreateProjectForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            account_permissions = AccountPermissionsModel(account=account)
            account_permissions.save()
            pr = AccountProjectModel(name_project=cd['name'])
            pr.save()
            pr.permissions.add(account_permissions)
            pr.users.add(account)
            pr.save()
    else:
        form = CreateProjectForm()
    return render(request,
                  'account/account.html',
                  {'account': account,
                   'form': form,
                   'list_projects': list_projects})


@login_required
def project(request, id):
    if not check_own_project(request, id):
        return redirect(account)
    prj_id = get_object_or_404(AccountProjectModel, id=id)
    return render(request,
                  'account/project.html',
                  {'prj_id': prj_id})


@login_required
def admin(request, id):
    if not check_own_project(request, id):
        return redirect(account)
    prj_id = get_object_or_404(AccountProjectModel, id=id)
    perm = prj_id.permissions.all()
    if request.method == 'POST' and prj_id.permissions.get(account=AccountModel.users.get(user=request.user)).admin:
        if "use" in request.POST:
            admin_form = EditAdminForm(id, request.POST)
            if admin_form.is_valid():
                cd = admin_form.cleaned_data
                choice_actions = cd['choice_actions']
                if choice_actions == "admin":
                    permm = AccountPermissionsModel.objects.get(id=cd['perm_id'].id)
                    permm.admin = not permm.admin
                    permm.save()
                if choice_actions == "device":
                    permm = AccountPermissionsModel.objects.get(id=cd['perm_id'].id)
                    permm.device = not permm.device
                    permm.save()
                if choice_actions == "del":
                    permm = AccountProjectModel.projects.get(id=id).permissions.get(id=cd['perm_id'].id)
                    AccountProjectModel.projects.get(id=id).permissions.remove(permm)
                    acc = AccountProjectModel.projects.get(id=id).users.get(id=cd['perm_id'].account.id)
                    AccountProjectModel.projects.get(id=id).users.remove(acc)
        else:
            admin_form = EditAdminForm(id)
        if "new" in request.POST:
            new_user = NewAdminUserForm(request.POST)
            if new_user.is_valid():
                cd = new_user.cleaned_data
                acc = AccountModel.users.get(user=get_user_model().objects.get(username=cd['new_user']))
                item = AccountProjectModel.projects.get(id=id)
                item.users.add(acc)
                p = AccountPermissionsModel(account=acc)
                p.save()
                item.permissions.add(p)
                item.save()
        else:
            new_user = NewAdminUserForm()
    else:
        new_user = NewAdminUserForm()
        admin_form = EditAdminForm(id)
    return render(request,
                  'account/admin.html',
                  {'prj_id': prj_id, 'admin_form': admin_form, 'perm': perm, 'new_user': new_user})


@login_required
def devices(request, id):
    if not check_own_project(request, id):
        return redirect(account)
    prj_id = get_object_or_404(AccountProjectModel, id=id)
    dvs = prj_id.devices.all()
    if request.method == 'POST' and prj_id.permissions.get(account=AccountModel.users.get(user=request.user)).device:
        create_form = CreateDeviceForm(request.POST)
        if create_form.is_valid():
            cd = create_form.cleaned_data
            device = AccountDevicesModel(name_device=cd['name'])
            device.save()
            prj_id.devices.add(device)
    else:
        create_form = CreateDeviceForm()
    return render(request,
                  'account/devices.html',
                  {'prj_id': prj_id, 'create_form': create_form, "dvs": dvs})