import numpy as np
import yaml

def load_data(yaml_file_path):
    with open(yaml_file_path,'r') as f:
        content = yaml.load(f.read())
    c = type('myobj', (object,), content)
    return c

def get_monthly_mortgage(
    loan_amount,
    loan_interest_rate,
    amortized_over_how_many_years,):
    
    monthly_mortgage_payment_markdown=\
    '''
    \begin{equation}
    c = \frac{rP(1+r)^N}{(1+r)^N-1}     ,r \neq 0;
    \end{equation}
    c = monthly payment  
    N = number of monthly payments  
    P = amount borrowed  
    r = monthly interest rate  
    r = (R/12)/100  
    R = annual interest rate  
    https://en.wikipedia.org/wiki/Mortgage_calculator
    '''
    
    monthly_interest_rate = loan_interest_rate/12
    amortized_over_how_many_months = 12*amortized_over_how_many_years
    monthly_mortgage_payment = \
        (monthly_interest_rate*loan_amount*(1+monthly_interest_rate)**amortized_over_how_many_months)/\
        ((1+monthly_interest_rate)**amortized_over_how_many_months-1)
    
    return monthly_mortgage_payment

def calculate(c, is_print=False):

    c.total_project_cost = \
        c.purchase_price \
        + c.purchase_closing_cost \
        + c.estimated_repair_cost
    

    c.down_payment_dollar = c.purchase_price*c.down_payment_of_purchase_price

    if c.down_payment_of_purchase_price == 1:
        c.loan_amount = 0
        c.monthly_mortgage_payment = 0        
    else:
        c.loan_amount = \
            c.purchase_price \
            - c.down_payment_dollar \
            - c.purchase_closing_cost


        c.monthly_mortgage_payment = get_monthly_mortgage(
            c.loan_amount,
            c.loan_interest_rate,
            c.amortized_over_how_many_years,)
    
    c.total_cash_needed = \
        c.down_payment_dollar \
        + c.estimated_repair_cost \
        + c.purchase_closing_cost \
        + c.point_charged_by_lender*c.loan_amount \
        + c.other_charges_from_the_lender
    
    if getattr(c,'line_of_credit',None):
        c.monthly_line_of_credit_payment = get_monthly_mortgage(
            c.total_cash_needed,
            c.line_of_credit['loan_interest_rate'],
            c.line_of_credit['amortized_over_how_many_years'])
        c.line_of_credit_payment = 0
    else:
        c.monthly_line_of_credit_payment = 0
        
    
    c.monthly_income = \
        c.total_gross_monthly_rent \
        + c.other_montly_income

    c.annual_property_tax = c.annual_property_taxes_prct*c.purchase_price
    c.monthly_property_tax = c.annual_property_tax / 12

    c.monthly_expenses = \
        + c.monthly_line_of_credit_payment \
        + c.monthly_mortgage_payment \
        + c.monthly_property_tax \
        + c.fixed_monthly_landlord_paid_expenses_electricity \
        + c.fixed_monthly_landlord_paid_expenses_water_sewer \
        + c.fixed_monthly_landlord_paid_expenses_pmi \
        + c.fixed_monthly_landlord_paid_expenses_garbage \
        + c.fixed_monthly_landlord_paid_expenses_hoas \
        + c.fixed_monthly_landlord_paid_expenses_insurance \
        + c.repairs_and_maintenance * c.monthly_income \
        + c.capital_expenditures * c.monthly_income \
        + c.management_fees * c.monthly_income \
        + c.vacancy * c.monthly_income\
        + c.other_monthly_expenses 

    
    c.monthly_cashflow = c.monthly_income - c.monthly_expenses
    
    c.net_operating_income = \
        12 * ( c.monthly_income \
        - c.monthly_expenses
        + c.monthly_line_of_credit_payment \
        + c.monthly_mortgage_payment \
        ) 
        
    c.purchase_cap_rate_prct = 100*c.net_operating_income/c.purchase_price
    
    if is_print:
        key_list = [
            # entered
            'purchase_price',
            'purchase_closing_cost',
            'estimated_repair_cost',
            # computed/
            'total_project_cost',
            'down_payment_dollar',
            'loan_amount',
            # entered
            'point_charged_by_lender',
            # computed
            'monthly_line_of_credit_payment',
            'monthly_mortgage_payment',
            'total_cash_needed',
            'monthly_income',
            'monthly_expenses',
            'monthly_cashflow',
            'net_operating_income',
            'purchase_cap_rate_prct',
        ]
        for k in key_list:
            if k.endswith('_prct'):
                print('{} {:1.2f}'.format(k,getattr(c,k)))
            else:
                print('{} {:1.0f}'.format(k,getattr(c,k)))

    return c