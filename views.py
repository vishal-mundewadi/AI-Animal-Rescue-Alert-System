from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from .models import AnimalReport


# -----------------------------
# Homepage view
# -----------------------------
def home(request):
    reports = AnimalReport.objects.all().order_by('-created_at')
    return render(request, 'rescue/home.html', {'reports': reports})


# -----------------------------
# View to display all reports
# -----------------------------
def reports(request):
    all_reports = AnimalReport.objects.all().order_by('-created_at')
    return render(request, 'rescue/reports.html', {'reports': all_reports})


# -----------------------------
# View for submitting new animal report
# -----------------------------
def report_form(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        animal_type = request.POST.get('animal_type', 'Other')
        description = request.POST.get('description', '').strip()
        location = request.POST.get('location', '')
        image = request.FILES.get('image')

        AnimalReport.objects.create(
            name=name,
            email=email,
            animal_type=animal_type,
            description=description,
            location=location,
            image=image
        )
        return redirect('reports')

    return render(request, 'rescue/report_form.html')


# -----------------------------
# Update report status + Send Email Notification
# -----------------------------
@csrf_exempt
def update_status(request, report_id):
    """
    Updates the rescue report status and sends acknowledgment emails.
    """
    if request.method == "POST":
        new_status = request.POST.get('status')

        try:
            report = AnimalReport.objects.get(id=report_id)
            report.status = new_status
            report.save()

            # ✅ Send automatic email notifications
            subject = ""
            message = ""

            if new_status == "Acknowledged":
                subject = "🐾 Rescue Team Acknowledged Your Report"
                message = (
                    f"Dear {report.name},\n\n"
                    f"We have received your report about the {report.animal_type} located at {report.location}.\n"
                    f"Our rescue team is on the way to help the animal.\n\n"
                    f"Description: {report.description}\n\n"
                    f"Thank you for caring for animals ❤️\n\n"
                    f"- AI Animal Rescue Team"
                )
            elif new_status == "Resolved":
                subject = "✅ Rescue Operation Completed"
                message = (
                    f"Dear {report.name},\n\n"
                    f"The rescue operation for the {report.animal_type} at {report.location} has been successfully completed.\n"
                    f"Thank you for reporting and helping save a life! 🐶🐱\n\n"
                    f"- AI Animal Rescue Team"
                )

            if subject and message:
                send_mail(
                    subject,
                    message,
                    "muvishal14@gmail.com",  # Sender (your email)
                    [report.email],         # Receiver (report submitter)
                    fail_silently=False,
                )

            return JsonResponse({'success': True})
        except AnimalReport.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Report not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})
