from django.urls import path
from . import views
from . import tax_paid_details_views
from . import salary_income_views
from . import other_income_views
from . import house_property_income_views
from . import interest_income_views
from . import dividend_views
from . import family_pension_views

urlpatterns = [
    # Unified POST and PUT API for TaxPaidDetails and document uploads
    path('tax-paid-details/create-or-update/', tax_paid_details_views.upsert_tax_paid_details,
         name='tax_paid_details_create_or_update'),

    # Retrieve TaxPaidDetails by service_request and group files by document_type
    path('tax-paid-details/', tax_paid_details_views.tax_paid_details_view,
         name='tax_paid_details_view'),

    # Delete a specific file (also deletes from S3)
    path('tax-paid-details/files/<int:file_id>/delete/', tax_paid_details_views.delete_tax_paid_file,
         name='delete_tax_paid_file'),

    path('personal-information/', views.personal_information_list,
         name='personal_information_list'),

    # Retrieve, update, or delete a specific PersonalInformation by primary key
    path('personal-information/<int:pk>/', views.personal_information_detail,
         name='personal_information_detail'),

    # Salary Income Details
    path('salary-income/', salary_income_views.salary_income_list,
         name='salary_income_list_create'),
    path('salary-income/<int:pk>/', salary_income_views.salary_income_detail,
         name='salary_income_detail_update'),
    path('salary-documents/<int:pk>/', salary_income_views.delete_salary_document,
         name='delete_salary_document_file'),
    path('salary-documents-count/<int:service_request_id>/', salary_income_views.salary_document_summary,
         name='salary_document_summary'),

    path('other-income-details/', other_income_views.other_income_details_list, name='other_income_details_list'),
    path('other-income-details/<int:pk>/', other_income_views.other_income_details_detail, name='other_income_details_detail'),

    path('other-income-documents/', other_income_views.add_other_income_document,
         name='add_other_income_document'),
    path('other-income-document/<int:pk>/', other_income_views.add_other_income_document,
         name='update_or_delete_other_income_document'),

    path('house-property-details/upsert/', house_property_income_views.upsert_house_property_details,
         name='upsert_house_property_details'),
    path('house-property-details/view/', house_property_income_views.house_property_details_view,
         name='house_property_details_view'),
    path('house-property-details/delete-file/<str:file_type>/<int:service_request_id>/',
         house_property_income_views.delete_house_property_file,
         name='delete_house_property_file'),

    # InterestIncome endpoints
    path('interest-income/upsert/', interest_income_views.upsert_interest_income, name='upsert_interest_income'),
    path('interest-income/get/', interest_income_views.get_interest_income, name='get_interest_income'),

    # InterestIncomeDocument endpoints
    path('interest-income-doc/add/', interest_income_views.add_interest_income_document,
         name='add_interest_income_document'),
    path('interest-income-doc/<int:document_id>/delete/', interest_income_views.delete_interest_income_document,
         name='delete_interest_income_document'),
    path('interest-income-doc/<int:document_id>/update/', interest_income_views.update_interest_income_document,
         name='update_interest_income_document'),

    path('dividend-income/', dividend_views.upsert_dividend_income, name='upsert_dividend_income'),  # POST create or update
    path('dividend-income/view/', dividend_views.get_dividend_income, name='get_dividend_income'),   # GET by service_request

    # DividendIncomeDocument APIs
    path('dividend-income/document/add/', dividend_views.add_dividend_income_document,
         name='add_dividend_income_document'),  # POST add doc
    path('dividend-income/document/<int:document_id>/update/', dividend_views.update_dividend_income_document,
         name='update_dividend_income_document'),  # PUT update doc
    path('dividend-income/document/<int:document_id>/delete/', dividend_views.delete_dividend_income_document,
         name='delete_dividend_income_document'),  # DELETE doc

    path('family-pension-income/', family_pension_views.upsert_family_pension_income,
         name='upsert_family_pension_income'),  # POST (create or update)
    path('family-pension-income/get/', family_pension_views.get_family_pension_income,
         name='get_family_pension_income'),     # GET (retrieve)

    # Family Pension Income Documents
    path('family-pension-income-documents/', family_pension_views.add_family_pension_income_document,
         name='add_family_pension_income_document'),  # POST (create)
    path('family-pension-income-documents/<int:document_id>/', family_pension_views.update_family_pension_income_document,
         name='update_family_pension_income_document'),  # PUT (update)
    path('family-pension-income-documents/<int:document_id>/delete/', family_pension_views.delete_family_pension_income_document,
         name='delete_family_pension_income_document'),  # DELETE

]

