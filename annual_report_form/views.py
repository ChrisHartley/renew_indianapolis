from django.shortcuts import render

from annual_report_form.forms import annualReportForm

# Displays form template for annual reports from property owners, and
# saves those submissions


def showAnnualReportForm(request):
    form = annualReportForm(request.POST or None)
    success = False
    if request.method == 'POST':
        form = annualReportForm(request.POST, request.FILES)
        if form.is_valid():
            # this is necessary so we can set the Property based on the parcel
            # number inputed
            form_saved = form.save(commit=False)
            form_saved.save()
            success = True
        else:
            pass
    return render(request, 'annual_report_form.html', {
        'form': form,
        'success': success,
        'title': "annual report"
    })
