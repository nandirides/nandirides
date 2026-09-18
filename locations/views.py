from decimal import Decimal, InvalidOperation
import csv
import io
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CountryForm, StateForm, CityForm, LocationForm
from .models import Country, State, City, Location
# ============================================================
# LOCATION DASHBOARD
# ============================================================
@login_required
@permission_required("locations.view_location", raise_exception=True)
def location_dashboard(request):
    country_count = Country.objects.count()
    state_count = State.objects.count()
    city_count = City.objects.count()
    location_count = Location.objects.count()
    mapped_locations = Location.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
    ).count()
    recent_locations = (
        Location.objects.select_related(
            "city",
            "city__state",
            "city__state__country",
        )
        .order_by("-created_at")[:10]
    )
    context = {
        "country_count": country_count,
        "state_count": state_count,
        "city_count": city_count,
        "location_count": location_count,
        "mapped_locations": mapped_locations,
        "recent_locations": recent_locations,
        "total_countries": country_count,
        "total_states": state_count,
        "total_cities": city_count,
        "total_locations": location_count,
    }
    return render(
        request,
        "locations/location_dashboard.html",
        context,
    )
# ============================================================
# LOCATION LIST
# ============================================================
@login_required
@permission_required("locations.view_location", raise_exception=True)
def location_list(request):
    locations = Location.objects.select_related(
        "city",
        "city__state",
        "city__state__country",
    ).order_by("-created_at")
    query = request.GET.get("q", "").strip()
    country_id = request.GET.get("country", "").strip()
    state_id = request.GET.get("state", "").strip()
    city_id = request.GET.get("city", "").strip()
    if query:
        locations = locations.filter(
            Q(address__icontains=query)
            | Q(city__name__icontains=query)
            | Q(city__state__name__icontains=query)
            | Q(city__state__country__name__icontains=query)
        )
    if country_id:
        locations = locations.filter(
            city__state__country_id=country_id
        )
    if state_id:
        locations = locations.filter(
            city__state_id=state_id
        )
    if city_id:
        locations = locations.filter(
            city_id=city_id
        )
    countries = Country.objects.order_by("name")
    states = State.objects.select_related(
        "country"
    ).order_by(
        "country__name",
        "name",
    )
    cities = City.objects.select_related(
        "state",
        "state__country",
    ).order_by(
        "state__country__name",
        "state__name",
        "name",
    )
    total_locations = Location.objects.count()
    total_cities = City.objects.count()
    mapped_locations = Location.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
    ).count()
    context = {
        "locations": locations,
        "countries": countries,
        "states": states,
        "cities": cities,
        "query": query,
        "selected_country": country_id,
        "selected_state": state_id,
        "selected_city": city_id,
        "total_locations": total_locations,
        "total_cities": total_cities,
        "mapped_locations": mapped_locations,
    }
    return render(
        request,
        "locations/location_list.html",
        context,
    )
# ============================================================
# LOCATION DETAIL
# ============================================================
@login_required
@permission_required("locations.view_location", raise_exception=True)
def location_detail(request, pk):
    location = get_object_or_404(
        Location.objects.select_related(
            "city",
            "city__state",
            "city__state__country",
        ),
        pk=pk,
    )
    context = {
        "location": location,
    }
    return render(
        request,
        "locations/location_detail.html",
        context,
    )
# ============================================================
# LOCATION MAP
# ============================================================
@login_required
@permission_required("locations.view_location", raise_exception=True)
def location_map(request, pk):
    location = get_object_or_404(
        Location.objects.select_related(
            "city",
            "city__state",
            "city__state__country",
        ),
        pk=pk,
    )
    context = {
        "location": location,
    }
    return render(
        request,
        "locations/location_map.html",
        context,
    )
# ============================================================
# LOCATION CREATE
# ============================================================
@login_required
@permission_required("locations.add_location", raise_exception=True)
def location_create(request):
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save()
            messages.success(
                request,
                f"Location '{location.address}' created successfully.",
            )
            return redirect("location_list")
    else:
        form = LocationForm()
    selected_country = (
        request.POST.get("country", "")
        if request.method == "POST"
        else ""
    )
    selected_state = (
        request.POST.get("state", "")
        if request.method == "POST"
        else ""
    )
    selected_city = (
        request.POST.get("city", "")
        if request.method == "POST"
        else ""
    )
    context = {
        "form": form,
        "location": None,
        "countries": Country.objects.order_by("name"),
        "selected_country": selected_country,
        "selected_state": selected_state,
        "selected_city": selected_city,
    }
    return render(
        request,
        "locations/location_form.html",
        context,
    )
# ============================================================
# LOCATION EDIT
# ============================================================
@login_required
@permission_required("locations.change_location", raise_exception=True)
def location_edit(request, pk):
    location = get_object_or_404(
        Location.objects.select_related(
            "city",
            "city__state",
            "city__state__country",
        ),
        pk=pk,
    )
    if request.method == "POST":
        form = LocationForm(
            request.POST,
            instance=location,
        )
        if form.is_valid():
            location = form.save()
            messages.success(
                request,
                f"Location '{location.address}' updated successfully.",
            )
            return redirect("location_list")
    else:
        form = LocationForm(
            instance=location,
        )
    selected_country = ""
    selected_state = ""
    selected_city = ""
    if location.city:
        selected_city = location.city_id
        selected_state = location.city.state_id
        selected_country = location.city.state.country_id
    if request.method == "POST":
        selected_country = request.POST.get(
            "country",
            selected_country,
        )
        selected_state = request.POST.get(
            "state",
            selected_state,
        )
        selected_city = request.POST.get(
            "city",
            selected_city,
        )
    context = {
        "form": form,
        "location": location,
        "countries": Country.objects.order_by("name"),
        "selected_country": selected_country,
        "selected_state": selected_state,
        "selected_city": selected_city,
    }
    return render(
        request,
        "locations/location_form.html",
        context,
    )
# ============================================================
# LOCATION DELETE
# ============================================================
@login_required
@permission_required("locations.delete_location", raise_exception=True)
def location_delete(request, pk):
    location = get_object_or_404(
        Location,
        pk=pk,
    )
    if request.method == "POST":
        location.delete()
        messages.success(
            request,
            "Location deleted successfully.",
        )
        return redirect("location_list")
    return redirect("location_list")
# ============================================================
# COUNTRY LIST
# ============================================================
@login_required
@permission_required("locations.view_country", raise_exception=True)
def country_list(request):
    query = request.GET.get(
        "q",
        "",
    ).strip()
    countries = Country.objects.annotate(
        state_count=Count(
            "states",
            distinct=True,
        ),
        city_count=Count(
            "states__cities",
            distinct=True,
        ),
        location_count=Count(
            "states__cities__locations",
            distinct=True,
        ),
    ).order_by("name")
    if query:
        countries = countries.filter(
            Q(name__icontains=query)
            | Q(code__icontains=query)
        )
    context = {
        "countries": countries,
        "query": query,
        "q": query,
    }
    return render(
        request,
        "locations/country_list.html",
        context,
    )
# ============================================================
# COUNTRY DETAIL
# ============================================================
@login_required
@permission_required("locations.view_country", raise_exception=True)
def country_detail(request, pk):
    country = get_object_or_404(
        Country,
        pk=pk,
    )
    states = country.states.annotate(
        city_count=Count(
            "cities",
            distinct=True,
        ),
        location_count=Count(
            "cities__locations",
            distinct=True,
        ),
    ).order_by("name")
    context = {
        "country": country,
        "states": states,
        "state_count": states.count(),
        "city_count": City.objects.filter(
            state__country=country
        ).count(),
        "location_count": Location.objects.filter(
            city__state__country=country
        ).count(),
    }
    return render(
        request,
        "locations/country_detail.html",
        context,
    )
# ============================================================
# COUNTRY CREATE
# ============================================================
@login_required
@permission_required("locations.add_country", raise_exception=True)
def country_create(request):
    if request.method == "POST":
        form = CountryForm(request.POST)
        if form.is_valid():
            country = form.save()
            messages.success(
                request,
                f"Country '{country.name}' created successfully.",
            )
            return redirect("country_list")
    else:
        form = CountryForm()
    context = {
        "form": form,
        "country": None,
    }
    return render(
        request,
        "locations/country_form.html",
        context,
    )
# ============================================================
# COUNTRY EDIT
# ============================================================
@login_required
@permission_required("locations.change_country", raise_exception=True)
def country_edit(request, pk):
    country = get_object_or_404(
        Country,
        pk=pk,
    )
    if request.method == "POST":
        form = CountryForm(
            request.POST,
            instance=country,
        )
        if form.is_valid():
            country = form.save()
            messages.success(
                request,
                f"Country '{country.name}' updated successfully.",
            )
            return redirect("country_list")
    else:
        form = CountryForm(
            instance=country,
        )
    context = {
        "form": form,
        "country": country,
    }
    return render(
        request,
        "locations/country_form.html",
        context,
    )
# ============================================================
# COUNTRY DELETE
# ============================================================
@login_required
@permission_required("locations.delete_country", raise_exception=True)
def country_delete(request, pk):
    country = get_object_or_404(
        Country,
        pk=pk,
    )
    if request.method == "POST":
        try:
            country.delete()
            messages.success(
                request,
                f"Country '{country.name}' deleted successfully.",
            )
        except Exception:
            messages.error(
                request,
                "Country cannot be deleted because it is being used.",
            )
        return redirect("country_list")
    return redirect("country_list")
# ============================================================
# STATE LIST
# ============================================================
@login_required
@permission_required("locations.view_state", raise_exception=True)
def state_list(request):
    query = request.GET.get(
        "q",
        "",
    ).strip()
    country_id = request.GET.get(
        "country",
        "",
    ).strip()
    states = State.objects.select_related(
        "country"
    ).annotate(
        city_count=Count(
            "cities",
            distinct=True,
        ),
        location_count=Count(
            "cities__locations",
            distinct=True,
        ),
    ).order_by(
        "country__name",
        "name",
    )
    if query:
        states = states.filter(
            Q(name__icontains=query)
            | Q(country__name__icontains=query)
        )
    if country_id:
        states = states.filter(
            country_id=country_id
        )
    context = {
        "states": states,
        "countries": Country.objects.order_by("name"),
        "query": query,
        "q": query,
        "selected_country": country_id,
    }
    return render(
        request,
        "locations/state_list.html",
        context,
    )
# ============================================================
# STATE DETAIL
# ============================================================
@login_required
@permission_required("locations.view_state", raise_exception=True)
def state_detail(request, pk):
    state = get_object_or_404(
        State.objects.select_related("country"),
        pk=pk,
    )
    cities = state.cities.annotate(
        location_count=Count(
            "locations",
            distinct=True,
        )
    ).order_by("name")
    context = {
        "state": state,
        "cities": cities,
        "city_count": cities.count(),
        "location_count": Location.objects.filter(
            city__state=state
        ).count(),
    }
    return render(
        request,
        "locations/state_detail.html",
        context,
    )
# ============================================================
# STATE CREATE
# ============================================================
@login_required
@permission_required("locations.add_state", raise_exception=True)
def state_create(request):
    if request.method == "POST":
        form = StateForm(request.POST)
        if form.is_valid():
            state = form.save()
            messages.success(
                request,
                f"State '{state.name}' created successfully.",
            )
            return redirect("state_list")
    else:
        form = StateForm()
    context = {
        "form": form,
        "state": None,
        "countries": Country.objects.order_by("name"),
        "selected_country": (
            request.POST.get("country", "")
            if request.method == "POST"
            else ""
        ),
    }
    return render(
        request,
        "locations/state_form.html",
        context,
    )
# ============================================================
# STATE EDIT
# ============================================================
@login_required
@permission_required("locations.change_state", raise_exception=True)
def state_edit(request, pk):
    state = get_object_or_404(
        State,
        pk=pk,
    )
    if request.method == "POST":
        form = StateForm(
            request.POST,
            instance=state,
        )
        if form.is_valid():
            state = form.save()
            messages.success(
                request,
                f"State '{state.name}' updated successfully.",
            )
            return redirect("state_list")
    else:
        form = StateForm(
            instance=state,
        )
    context = {
        "form": form,
        "state": state,
        "countries": Country.objects.order_by("name"),
        "selected_country": (
            request.POST.get(
                "country",
                state.country_id,
            )
            if request.method == "POST"
            else state.country_id
        ),
    }
    return render(
        request,
        "locations/state_form.html",
        context,
    )
# ============================================================
# STATE DELETE
# ============================================================
@login_required
@permission_required("locations.delete_state", raise_exception=True)
def state_delete(request, pk):
    state = get_object_or_404(
        State,
        pk=pk,
    )
    if request.method == "POST":
        try:
            state.delete()
            messages.success(
                request,
                f"State '{state.name}' deleted successfully.",
            )
        except Exception:
            messages.error(
                request,
                "State cannot be deleted because it is being used.",
            )
        return redirect("state_list")
    return redirect("state_list")
# ============================================================
# CITY LIST
# ============================================================
@login_required
@permission_required("locations.view_city", raise_exception=True)
def city_list(request):
    query = request.GET.get(
        "q",
        "",
    ).strip()
    country_id = request.GET.get(
        "country",
        "",
    ).strip()
    state_id = request.GET.get(
        "state",
        "",
    ).strip()
    cities = City.objects.select_related(
        "state",
        "state__country",
    ).annotate(
        location_count=Count(
            "locations",
            distinct=True,
        )
    ).order_by(
        "state__country__name",
        "state__name",
        "name",
    )
    if query:
        cities = cities.filter(
            Q(name__icontains=query)
            | Q(state__name__icontains=query)
            | Q(state__country__name__icontains=query)
        )
    if country_id:
        cities = cities.filter(
            state__country_id=country_id
        )
    if state_id:
        cities = cities.filter(
            state_id=state_id
        )
    context = {
        "cities": cities,
        "countries": Country.objects.order_by("name"),
        "states": State.objects.select_related(
            "country"
        ).order_by(
            "country__name",
            "name",
        ),
        "query": query,
        "q": query,
        "selected_country": country_id,
        "selected_state": state_id,
    }
    return render(
        request,
        "locations/city_list.html",
        context,
    )
# ============================================================
# CITY DETAIL
# ============================================================
@login_required
@permission_required("locations.view_city", raise_exception=True)
def city_detail(request, pk):
    city = get_object_or_404(
        City.objects.select_related(
            "state",
            "state__country",
        ),
        pk=pk,
    )
    locations = city.locations.order_by(
        "-created_at"
    )
    context = {
        "city": city,
        "locations": locations,
        "location_count": locations.count(),
    }
    return render(
        request,
        "locations/city_detail.html",
        context,
    )
# ============================================================
# CITY CREATE
# ============================================================
@login_required
@permission_required("locations.add_city", raise_exception=True)
def city_create(request):
    if request.method == "POST":
        form = CityForm(request.POST)
        country_id = request.POST.get(
            "country",
            "",
        ).strip()
        state_id = request.POST.get(
            "state",
            "",
        ).strip()
        if country_id:
            form.fields["state"].queryset = State.objects.filter(
                country_id=country_id
            ).order_by("name")
        if form.is_valid():
            state = form.cleaned_data.get("state")
            if not state:
                form.add_error(
                    "state",
                    "Please select a state.",
                )
            elif country_id and str(state.country_id) != str(country_id):
                form.add_error(
                    "state",
                    "Selected state does not belong to the selected country.",
                )
            elif City.objects.filter(
                state=state,
                name__iexact=form.cleaned_data["name"],
            ).exists():
                form.add_error(
                    "name",
                    "City already exists in the selected state.",
                )
            else:
                city = form.save()
                messages.success(
                    request,
                    f"City '{city.name}' created successfully.",
                )
                return redirect("city_list")
    else:
        form = CityForm()
        country_id = ""
        state_id = ""
    context = {
        "form": form,
        "city": None,
        "countries": Country.objects.order_by("name"),
        "states": form.fields["state"].queryset,
        "selected_country": country_id,
        "selected_state": state_id,
    }
    return render(
        request,
        "locations/city_form.html",
        context,
    )
# ============================================================
# CITY EDIT
# ============================================================
@login_required
@permission_required("locations.change_city", raise_exception=True)
def city_edit(request, pk):
    city = get_object_or_404(
        City.objects.select_related(
            "state",
            "state__country",
        ),
        pk=pk,
    )
    if request.method == "POST":
        form = CityForm(
            request.POST,
            instance=city,
        )
        country_id = request.POST.get(
            "country",
            "",
        ).strip()
        state_id = request.POST.get(
            "state",
            "",
        ).strip()
        if country_id:
            form.fields["state"].queryset = State.objects.filter(
                country_id=country_id
            ).order_by("name")
        if form.is_valid():
            state = form.cleaned_data.get("state")
            if not state:
                form.add_error(
                    "state",
                    "Please select a state.",
                )
            elif country_id and str(state.country_id) != str(country_id):
                form.add_error(
                    "state",
                    "Selected state does not belong to the selected country.",
                )
            elif City.objects.filter(
                state=state,
                name__iexact=form.cleaned_data["name"],
            ).exclude(
                pk=pk
            ).exists():
                form.add_error(
                    "name",
                    "City already exists in the selected state.",
                )
            else:
                city = form.save()
                messages.success(
                    request,
                    f"City '{city.name}' updated successfully.",
                )
                return redirect("city_list")
    else:
        form = CityForm(
            instance=city,
        )
        country_id = city.state.country_id
        state_id = city.state_id
        form.fields["state"].queryset = State.objects.filter(
            country_id=country_id
        ).order_by("name")
    context = {
        "form": form,
        "city": city,
        "countries": Country.objects.order_by("name"),
        "states": form.fields["state"].queryset,
        "selected_country": country_id,
        "selected_state": state_id,
    }
    return render(
        request,
        "locations/city_form.html",
        context,
    )
# ============================================================
# CITY DELETE
# ============================================================
@login_required
@permission_required("locations.delete_city", raise_exception=True)
def city_delete(request, pk):
    city = get_object_or_404(
        City,
        pk=pk,
    )
    if request.method == "POST":
        try:
            city.delete()
            messages.success(
                request,
                f"City '{city.name}' deleted successfully.",
            )
        except Exception:
            messages.error(
                request,
                "City could not be deleted.",
            )
        return redirect("city_list")
    return redirect("city_list")
# ============================================================
# AJAX: STATES BY COUNTRY
# ============================================================
@login_required
@permission_required("locations.view_state", raise_exception=True)
def states_by_country(request):
    country_id = request.GET.get(
        "country",
        "",
    ).strip()
    if not country_id:
        return JsonResponse(
            {"states": []}
        )
    states = State.objects.filter(
        country_id=country_id
    ).order_by("name")
    return JsonResponse(
        {
            "states": [
                {
                    "id": state.id,
                    "name": state.name,
                }
                for state in states
            ]
        }
    )
# ============================================================
# AJAX: CITIES BY STATE
# ============================================================
@login_required
@permission_required("locations.view_city", raise_exception=True)
def cities_by_state(request):
    state_id = request.GET.get(
        "state",
        "",
    ).strip()
    if not state_id:
        return JsonResponse(
            {"cities": []}
        )
    cities = City.objects.filter(
        state_id=state_id
    ).order_by("name")
    return JsonResponse(
        {
            "cities": [
                {
                    "id": city.id,
                    "name": city.name,
                }
                for city in cities
            ]
        }
    )
# ============================================================
# LOCATION IMPORT
# ============================================================
@login_required
@permission_required("locations.add_location", raise_exception=True)
def location_import(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            messages.error(
                request,
                "Please select a CSV file.",
            )
            return redirect("location_import")
        if not uploaded_file.name.lower().endswith(".csv"):
            messages.error(
                request,
                "Only CSV files are supported.",
            )
            return redirect("location_import")
        try:
            content = uploaded_file.read().decode(
                "utf-8-sig"
            )
            reader = csv.DictReader(
                io.StringIO(content)
            )
            required_columns = {
                "address",
                "country",
                "state",
                "city",
                "latitude",
                "longitude",
            }
            headers = {
                header.strip().lower()
                for header in (reader.fieldnames or [])
                if header
            }
            missing_columns = required_columns - headers
            if missing_columns:
                messages.error(
                    request,
                    "Missing required columns: "
                    + ", ".join(
                        sorted(missing_columns)
                    ),
                )
                return redirect("location_import")
            created_count = 0
            skipped_count = 0
            for row in reader:
                address = (
                    row.get("address") or ""
                ).strip()
                country_name = (
                    row.get("country") or ""
                ).strip()
                state_name = (
                    row.get("state") or ""
                ).strip()
                city_name = (
                    row.get("city") or ""
                ).strip()
                latitude = (
                    row.get("latitude") or ""
                ).strip()
                longitude = (
                    row.get("longitude") or ""
                ).strip()
                if not address or not country_name or not state_name:
                    skipped_count += 1
                    continue
                country = Country.objects.filter(
                    name__iexact=country_name
                ).first()
                if not country:
                    country_code = country_name[:10].upper()
                    existing_code = Country.objects.filter(
                        code__iexact=country_code
                    ).exists()
                    if existing_code:
                        country_code = (
                            country_name[:7].upper()
                            + str(Country.objects.count() + 1)
                        )[:10]
                    country = Country.objects.create(
                        name=country_name,
                        code=country_code,
                    )
                state = State.objects.filter(
                    country=country,
                    name__iexact=state_name,
                ).first()
                if not state:
                    state = State.objects.create(
                        country=country,
                        name=state_name,
                    )
                city = None
                if city_name:
                    city = City.objects.filter(
                        state=state,
                        name__iexact=city_name,
                    ).first()
                    if not city:
                        city = City.objects.create(
                            state=state,
                            name=city_name,
                        )
                try:
                    latitude_value = Decimal(latitude)
                    longitude_value = Decimal(longitude)
                except (InvalidOperation, ValueError):
                    skipped_count += 1
                    continue
                if (
                    latitude_value < Decimal("-90")
                    or latitude_value > Decimal("90")
                    or longitude_value < Decimal("-180")
                    or longitude_value > Decimal("180")
                ):
                    skipped_count += 1
                    continue
                Location.objects.create(
                    address=address,
                    city=city,
                    latitude=latitude_value,
                    longitude=longitude_value,
                )
                created_count += 1
            messages.success(
                request,
                f"{created_count} location(s) imported successfully.",
            )
            if skipped_count:
                messages.warning(
                    request,
                    f"{skipped_count} row(s) were skipped.",
                )
        except UnicodeDecodeError:
            messages.error(
                request,
                "Unable to read the CSV file. Please use UTF-8 encoding.",
            )
        except Exception as exc:
            messages.error(
                request,
                f"Import failed: {exc}",
            )
        return redirect("location_list")
    return render(
        request,
        "locations/location_import.html",
    )
