from django.urls import path

from apps.reports import views

urlpatterns = [
    path("reports/sales", views.SalesReportView.as_view(), name="report-sales"),
    path("reports/sales/daily", views.SalesDailyView.as_view(), name="report-sales-daily"),
    path("reports/best-sellers", views.BestSellersView.as_view(), name="report-best-sellers"),
    path("reports/profit", views.ProfitReportView.as_view(), name="report-profit"),
]
