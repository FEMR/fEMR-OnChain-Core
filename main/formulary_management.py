import csv
from main.csvio.added_inventory import AddedInventoryHandler
from main.csvio.initial_inventory import InitialInventoryHandler
import chardet

from django.http.response import HttpResponse
from main.forms import AddSupplyForm, CSVUploadForm, InventoryEntryForm, RemoveSupplyForm
from main.models import CSVUploadDocument, Campaign, InventoryCategory, InventoryEntry, InventoryForm, Manufacturer, Medication
from django.shortcuts import redirect, render
from django.db.models.query_utils import Q


def formulary_home_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') |
                                      Q(name='Organization Admin') |
                                      Q(name='Operation Admin')).exists():
            campaign = Campaign.objects.get(name=request.session['campaign'])
            formulary = campaign.inventory.entries.all().order_by('medication')
            return render(request, 'formulary/home.html', {'page_name': 'Inventory',
                                                           'list_view': formulary})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def add_supply_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') |
                                      Q(name='Organization Admin') |
                                      Q(name='Operation Admin')).exists():
            if request.method == "GET":
                form = InventoryEntryForm()
            else:
                form = InventoryEntryForm(request.POST)
                t = form.save()
                t.save()
            return render(request, 'formulary/add_supply.html', {'form': form})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def edit_add_supply_view(request, id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') |
                                      Q(name='Organization Admin') |
                                      Q(name='Operation Admin')).exists():
            inventory_entry = InventoryEntry.objects.get(pk=id)
            if request.method == "GET":
                form = AddSupplyForm()
                return render(request, 'formulary/edit_add_supply.html', {'page_name': inventory_entry, 'form': form, 'item_id': inventory_entry.id})
            elif request.method == "POST":
                form = AddSupplyForm(request.POST)
                if form.is_valid():
                    inventory_entry.initial_quantity = inventory_entry.initial_quantity + \
                        int(request.POST['quantity'])
                    inventory_entry.quantity = inventory_entry.quantity + \
                        int(request.POST['quantity'])
                    inventory_entry.save()
                    return redirect('main:formulary_home_view')
                else:
                    return render(request, 'formulary/edit_add_supply.html', {'page_name': inventory_entry, 'form': form, 'item_id': inventory_entry.id})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def edit_sub_supply_view(request, id=None):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') |
                                      Q(name='Organization Admin') |
                                      Q(name='Operation Admin')).exists():
            inventory_entry = InventoryEntry.objects.get(pk=id)
            if request.method == "GET":
                form = RemoveSupplyForm()
                return render(request, 'formulary/edit_sub_supply.html', {'page_name': inventory_entry, 'form': form, 'item_id': inventory_entry.id})
            elif request.method == "POST":
                form = AddSupplyForm(request.POST)
                if form.is_valid():
                    if inventory_entry.initial_quantity > int(request.POST['quantity']) and inventory_entry.quantity > int(request.POST['quantity']):
                        inventory_entry.initial_quantity = inventory_entry.initial_quantity - \
                            int(request.POST['quantity'])
                        inventory_entry.quantity = inventory_entry.quantity - \
                            int(request.POST['quantity'])
                    else:
                        inventory_entry.initial_quantity = 0
                        inventory_entry.quantity = 0
                    inventory_entry.save()
                    return redirect('main:formulary_home_view')
                else:
                    return render(request, 'formulary/edit_add_supply.html', {'page_name': inventory_entry, 'form': form, 'item_id': inventory_entry.id})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def csv_handler_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') |
                                      Q(name='Organization Admin') |
                                      Q(name='Operation Admin')).exists():
            return render(request, 'formulary/csv_handler.html', {'form': CSVUploadForm()})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def csv_import_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') |
                                      Q(name='Organization Admin') |
                                      Q(name='Operation Admin')).exists():
            campaign = Campaign.objects.get(name=request.session['campaign'])
            form = CSVUploadForm(request.POST, request.FILES)
            result = ""
            if form.is_valid():
                print("Form is valid.")

                upload = CSVUploadDocument.objects.create(document=request.FILES['upload'])

                if request.POST['mode_option'] == "1":
                    InitialInventoryHandler().read(upload, campaign)
                elif request.POST['mode_option'] == "2":
                    AddedInventoryHandler().read(upload, campaign)
                upload.document.delete()
                upload.delete()
                return render(request, 'formulary/csv_import.html', {'result': 'Formulary uploaded successfully.'})
            else:
                print("Form not valid.")
                return render(request, 'formulary/csv_handler.html', {'form': form, 'result': result})
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')


def csv_export_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(Q(name='Campaign Manager') |
                                      Q(name='Organization Admin') |
                                      Q(name='Operation Admin')).exists():
            campaign = Campaign.objects.get(name=request.session['campaign'])
            formulary = campaign.inventory.entries.all().order_by('medication')
            response = HttpResponse(
                content_type='text/csv',
                headers={
                    'Content-Disposition': 'attachment; filename="formulary.csv"'},
            )
            handler = InitialInventoryHandler()
            return handler.write(response, formulary)
        else:
            return redirect('main:permission_denied')
    else:
        return redirect('main:not_logged_in')
