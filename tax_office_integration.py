import re
from typing import List, Optional, Union, Any, get_type_hints
from enum import Enum
from pydantic import BaseModel
from dataclasses import dataclass
import xml.dom.minidom
import xml.etree.ElementTree as ET



def convert_field_name(name):
    if "_" in name:
        parts = name.split("_")
        parts = [part.capitalize() if i > 0 else part for i, part in enumerate(parts)]
        name = "".join(parts)
    return name


def object_to_xml(obj):
    impl = xml.dom.minidom.getDOMImplementation()
    dom = impl.createDocument(None, obj.__class__.__name__, None)
    root_element = dom.documentElement

    type_hints = obj.__annotations__
    for key, value in obj.__dict__.items():
        if isinstance(value, (str, int, float)):
            field = type_hints.get(key)
            element_name = convert_field_name(key)
            child_element = dom.createElement(element_name)
            child_element.appendChild(dom.createTextNode(str(value)))
            root_element.appendChild(child_element)
        elif isinstance(value, list):
            field = type_hints.get(key)
            element_name = field.field_info.alias or convert_field_name(key)
            list_element = dom.createElement(element_name)
            for item in value:
                item_element = dom.createElement(item.__class__.__name__)
                item_element.appendChild(dom.createTextNode(object_to_xml(item)))
                list_element.appendChild(item_element)
            root_element.appendChild(list_element)
        elif isinstance(value, object):
            child_element = dom.createElement(key)
            child_element.appendChild(dom.createTextNode(object_to_xml(value)))
            root_element.appendChild(child_element)

    xml_string = dom.toprettyxml(indent="  ")
    with open("output.xml", "w") as file:
        file.write(xml_string)
    return xml_string

class Article:
    art_id: int
    date_of_entry: str
    art_group_id: int
    art_desc: str

    def __init__(self, art_id: int, date_of_entry: str, art_group_id: int, art_desc: str) -> None:
        self.art_id = art_id
        self.date_of_entry = date_of_entry
        self.art_group_id = art_group_id
        self.art_desc = art_desc


class Articles:
    article: List[Article]

    def __init__(self, article: List[Article]) -> None:
        self.article = article


class Basic:
    basic_type: str
    """
    Mã hai chữ số cho biết loại dữ liệu chính
    mà phần tử mô tả. Xem tài liệu "Norwegian SAF-T Cash
    Đăng ký dữ liệu - Danh sách mã" trên SAF-T Cash
    đăng ký trang tài liệu cho một danh sách
    các giá trị liệt kê.
    """
    basic_id: str
    """
    Mã duy nhất cho cấu trúc riêng lẻ (điển hình
    hệ thống cụ thể)
    """
    predefined_basic_id: Optional[str]
    """
    Mã 5 chữ số được xác định trước được bao gồm ngoài
    vào basicID (hệ thống cụ thể) của chính công ty.
    Khi sử dụng mã này, ánh xạ có thể được thực hiện
    giữa basicID cụ thể của hệ thống với tiêu chuẩn
    mã xác định.
    Xem tài liệu "Norwegian SAF-T Cash
    Đăng ký dữ liệu - Danh sách mã" trên SAF-T Cash
    đăng ký trang tài liệu cho danh sách liệt kê
    các giá trị.
    """
    basic_desc: str
    """
    Mô tả cụ thể của hệ thống về cấu trúc tổng thể
    """

    def __init__(self, basic_type: str, basic_id: str, predefined_basic_id: Optional[str], basic_desc: str) -> None:
        self.basic_type = basic_type
        self.basic_id = basic_id
        self.predefined_basic_id = predefined_basic_id
        self.basic_desc = basic_desc


class Basics:
    basic: List[Basic]

    def __init__(self, basic: List[Basic]) -> None:
        self.basic = basic


class EmployeeRole:
    role_type: str
    role_type_desc: Optional[str]

    def __init__(self, role_type: str, role_type_desc: Optional[str]) -> None:
        self.role_type = role_type
        self.role_type_desc = role_type_desc


class Employee:
    emp_id: int
    date_of_entry: str
    time_of_entry: str
    first_name: str
    sur_name: str
    employee_role: EmployeeRole

    def __init__(self, emp_id: int, date_of_entry: str, time_of_entry: str, first_name: str, sur_name: str,
                 employee_role: EmployeeRole) -> None:
        self.emp_id = emp_id
        self.date_of_entry = date_of_entry
        self.time_of_entry = time_of_entry
        self.first_name = first_name
        self.sur_name = sur_name
        self.employee_role = employee_role


class Employees:
    employee: List[Employee]

    def __init__(self, employee: List[Employee]) -> None:
        self.employee = employee


class AmntTp(Enum):
    C = "C"
    D = "D"


class VatElement:
    vat_code: int
    vat_perc: str
    vat_amnt: str
    vat_amnt_tp: AmntTp
    vat_bas_amnt: Optional[str]
    cash_sale_amnt: Optional[str]

    def __init__(self, vat_code: int, vat_perc: str, vat_amnt: str, vat_amnt_tp: AmntTp, vat_bas_amnt: Optional[str],
                 cash_sale_amnt: Optional[str]) -> None:
        self.vat_code = vat_code
        self.vat_perc = vat_perc
        self.vat_amnt = vat_amnt
        self.vat_amnt_tp = vat_amnt_tp
        self.vat_bas_amnt = vat_bas_amnt
        self.cash_sale_amnt = cash_sale_amnt


class CTLineElement:
    nr: int
    line_id: int
    line_type: str
    art_group_id: int
    art_id: int
    qnt: int
    line_amnt_in: str
    line_amnt_ex: str
    amnt_tp: AmntTp
    emp_id: int
    line_date: str
    line_time: str
    vat: VatElement

    def __init__(self, nr: int, line_id: int, line_type: str, art_group_id: int, art_id: int, qnt: int,
                 line_amnt_in: str, line_amnt_ex: str, amnt_tp: AmntTp, emp_id: int, line_date: str,
                 line_time: str, vat: VatElement) -> None:
        self.nr = nr
        self.line_id = line_id
        self.line_type = line_type
        self.art_group_id = art_group_id
        self.art_id = art_id
        self.qnt = qnt
        self.line_amnt_in = line_amnt_in
        self.line_amnt_ex = line_amnt_ex
        self.amnt_tp = amnt_tp
        self.emp_id = emp_id
        self.line_date = line_date
        self.line_time = line_time
        self.vat = vat


class Payment:
    payment_type: str
    paid_amnt: str
    emp_id: int
    cur_code: str
    exch_rt: str
    payment_ref_id: str

    def __init__(self, payment_type: str, paid_amnt: str, emp_id: int, cur_code: str, exch_rt: str,
                 payment_ref_id: str) -> None:
        self.payment_type = payment_type
        self.paid_amnt = paid_amnt
        self.emp_id = emp_id
        self.cur_code = cur_code
        self.exch_rt = exch_rt
        self.payment_ref_id = payment_ref_id


class Rounding:
    rounding_amnt: str
    acc_id: Optional[str]

    def __init__(self, rounding_amnt: str) -> None:
        self.rounding_amnt = rounding_amnt


class Cashtransaction:
    """
    Phần tử giao dịch tiền mặt chứa dữ liệu về một giao dịch mà máy tính tiền được sử dụng.
    """
    nr: int
    """
    Số giao dịch, cũng được sử dụng làm tham chiếu đến
    ct_line - nr - element.
    """
    trans_id: int
    """
    ID giao dịch. Nội bộ độc đáo khác, tuần tự
    ID được sử dụng bởi hệ thống máy tính tiền. Nếu hệ thống
    không có ID như vậy, đây có thể là
    tương đương với phần tử “nr”.
    """
    trans_type: str
    """
    Loại giao dịch. Mô tả của mã phải được
    được khai báo trong bảng 'Basics'
    """
    trans_amnt_in: str
    """
    Số tiền liên quan đến giao dịch, bao gồm
    thuế GTGT.
    Định dạng của phần tử này phải giống hệt với
    định dạng được sử dụng để tạo hàm băm và chữ ký.
    Xem “Yêu cầu và hướng dẫn cho
    triển khai chữ ký số trong máy tính tiền
    Hệ thống” trên máy tính tiền SAF-T
    trang tài liệu.
    """
    trans_amnt_ex: str
    """
    Số tiền liên quan đến giao dịch, không bao gồm
    thuế GTGT.
    """
    amnt_tp: AmntTp
    emp_id: int
    period_number: int
    trans_date: str
    trans_time: str
    ct_line: List[CTLineElement]
    vat: List[VatElement]
    rounding: Rounding
    payment: Payment
    signature: str
    key_version: int
    receipt_num: int
    receipt_copy_num: int
    receipt_proforma_num: int
    receipt_delivery_num: int
    void_transaction: bool
    training_id: bool


class ReportArtGroup:
    art_group_id: int
    art_group_num: int
    art_group_amnt: str
    emp_id: Optional[int]

    def __init__(self, art_group_id: int, art_group_num: int, art_group_amnt: str, emp_id: Optional[int]) -> None:
        self.art_group_id = art_group_id
        self.art_group_num = art_group_num
        self.art_group_amnt = art_group_amnt
        self.emp_id = emp_id


class ReportArtGroups:
    report_art_group: List[ReportArtGroup]

    def __init__(self, report_art_group: List[ReportArtGroup]) -> None:
        self.report_art_group = report_art_group


class ReportCashSalesVat:
    report_cash_sale_vat: List[VatElement]

    def __init__(self, report_cash_sale_vat: List[VatElement]) -> None:
        self.report_cash_sale_vat = report_cash_sale_vat


class ReportCorrLine:
    corr_line_type: str
    corr_line_num: int
    corr_line_amnt: str

    def __init__(self, corr_line_type: str, corr_line_num: int, corr_line_amnt: str) -> None:
        self.corr_line_type = corr_line_type
        self.corr_line_num = corr_line_num
        self.corr_line_amnt = corr_line_amnt


class ReportCorrLines:
    report_corr_line: ReportCorrLine

    def __init__(self, report_corr_line: ReportCorrLine) -> None:
        self.report_corr_line = report_corr_line


class ReportCreditMemos:
    credit_memos_num: int
    credit_memos_amnt: str

    def __init__(self, credit_memos_num: int, credit_memos_amnt: str) -> None:
        self.credit_memos_num = credit_memos_num
        self.credit_memos_amnt = credit_memos_amnt


class ReportCreditSales:
    credit_sales_num: int
    credit_sales_amnt: str

    def __init__(self, credit_sales_num: int, credit_sales_amnt: str) -> None:
        self.credit_sales_num = credit_sales_num
        self.credit_sales_amnt = credit_sales_amnt


class ReportEmpArtGroups:
    report_emp_art_group: List[ReportArtGroup]

    def __init__(self, report_emp_art_group: List[ReportArtGroup]) -> None:
        self.report_emp_art_group = report_emp_art_group


class ReportEmpOpeningChangeFloat:
    emp_id: int
    opening_change_float_amnt: str

    def __init__(self, emp_id: int, opening_change_float_amnt: str) -> None:
        self.emp_id = emp_id
        self.opening_change_float_amnt = opening_change_float_amnt


class ReportEmpOpeningChangeFloats:
    report_emp_opening_change_float: List[ReportEmpOpeningChangeFloat]

    def __init__(self, report_emp_opening_change_float: List[ReportEmpOpeningChangeFloat]) -> None:
        self.report_emp_opening_change_float = report_emp_opening_change_float


class ReportPayment:
    emp_id: Optional[int]
    payment_type: str
    payment_num: int
    payment_amnt: str

    def __init__(self, emp_id: Optional[int], payment_type: str, payment_num: int, payment_amnt: str) -> None:
        self.emp_id = emp_id
        self.payment_type = payment_type
        self.payment_num = payment_num
        self.payment_amnt = payment_amnt


class ReportEmpPayments:
    report_emp_payment: List[ReportPayment]

    def __init__(self, report_emp_payment: List[ReportPayment]) -> None:
        self.report_emp_payment = report_emp_payment


class ReportOtherCorr:
    other_corr_type: str
    other_corr_num: int
    other_corr_amnt: str

    def __init__(self, other_corr_type: str, other_corr_num: int, other_corr_amnt: str) -> None:
        self.other_corr_type = other_corr_type
        self.other_corr_num = other_corr_num
        self.other_corr_amnt = other_corr_amnt


class ReportOtherCorrs:
    report_other_corr: ReportOtherCorr

    def __init__(self, report_other_corr: ReportOtherCorr) -> None:
        self.report_other_corr = report_other_corr


class ReportPayIn:
    pay_in_type: str
    pay_in_num: int
    pay_in_amnt: str

    def __init__(self, pay_in_type: str, pay_in_num: int, pay_in_amnt: str) -> None:
        self.pay_in_type = pay_in_type
        self.pay_in_num = pay_in_num
        self.pay_in_amnt = pay_in_amnt


class ReportPayIns:
    report_pay_in: ReportPayIn

    def __init__(self, report_pay_in: ReportPayIn) -> None:
        self.report_pay_in = report_pay_in


class ReportPayOut:
    pay_out_type: str
    pay_out_num: int
    pay_out_amnt: str

    def __init__(self, pay_out_type: str, pay_out_num: int, pay_out_amnt: str) -> None:
        self.pay_out_type = pay_out_type
        self.pay_out_num = pay_out_num
        self.pay_out_amnt = pay_out_amnt


class ReportPayOuts:
    report_pay_out: ReportPayOut

    def __init__(self, report_pay_out: ReportPayOut) -> None:
        self.report_pay_out = report_pay_out


class ReportPayments:
    report_payment: List[ReportPayment]

    def __init__(self, report_payment: List[ReportPayment]) -> None:
        self.report_payment = report_payment


class ReportPriceInquiry:
    price_inquiry_group: int
    price_inquiry_num: int
    price_inquiry_amnt: str

    def __init__(self, price_inquiry_group: int, price_inquiry_num: int, price_inquiry_amnt: str) -> None:
        self.price_inquiry_group = price_inquiry_group
        self.price_inquiry_num = price_inquiry_num
        self.price_inquiry_amnt = price_inquiry_amnt


class ReportPriceInquiries:
    report_price_inquiry: ReportPriceInquiry

    def __init__(self, report_price_inquiry: ReportPriceInquiry) -> None:
        self.report_price_inquiry = report_price_inquiry


class ReportTotalCashSales:
    total_cash_sale_amnt: str

    def __init__(self, total_cash_sale_amnt: str) -> None:
        self.total_cash_sale_amnt = total_cash_sale_amnt


class EventReport:
    report_id: int
    report_type: str
    company_ident: int
    company_name: str
    report_date: str
    report_time: str
    register_id: str
    report_total_cash_sales: ReportTotalCashSales
    report_art_groups: ReportArtGroups
    report_emp_art_groups: ReportEmpArtGroups
    report_payments: ReportPayments
    report_emp_payments: ReportEmpPayments
    report_cash_sales_vat: ReportCashSalesVat
    report_opening_change_float: str
    report_emp_opening_change_floats: ReportEmpOpeningChangeFloats
    report_receipt_num: int
    report_open_cash_box_num: int
    report_receipt_copy_num: int
    report_receipt_copy_amnt: str
    report_receipt_proforma_num: int
    report_receipt_proforma_amnt: str
    report_return_num: int
    report_return_amnt: str
    report_discount_num: int
    report_discount_amnt: str
    report_void_trans_num: int
    report_void_trans_amnt: str
    report_corr_lines: ReportCorrLines
    report_price_inquiries: ReportPriceInquiries
    report_other_corrs: ReportOtherCorrs
    report_receipt_delivery_num: int
    report_receipt_delivery_amnt: str
    report_training_num: int
    report_training_amnt: str
    report_credit_sales: ReportCreditSales
    report_credit_memos: ReportCreditMemos
    report_pay_ins: ReportPayIns
    report_pay_outs: ReportPayOuts
    report_grand_total_sales: str
    report_grand_total_return: str
    report_grand_total_sales_net: str

    def __init__(self, report_id: int, report_type: str, company_ident: int, company_name: str, report_date: str,
                 report_time: str, register_id: str, report_total_cash_sales: ReportTotalCashSales,
                 report_art_groups: ReportArtGroups, report_emp_art_groups: ReportEmpArtGroups,
                 report_payments: ReportPayments, report_emp_payments: ReportEmpPayments,
                 report_cash_sales_vat: ReportCashSalesVat, report_opening_change_float: str,
                 report_emp_opening_change_floats: ReportEmpOpeningChangeFloats, report_receipt_num: int,
                 report_open_cash_box_num: int, report_receipt_copy_num: int, report_receipt_copy_amnt: str,
                 report_receipt_proforma_num: int, report_receipt_proforma_amnt: str, report_return_num: int,
                 report_return_amnt: str, report_discount_num: int, report_discount_amnt: str,
                 report_void_trans_num: int, report_void_trans_amnt: str, report_corr_lines: ReportCorrLines,
                 report_price_inquiries: ReportPriceInquiries, report_other_corrs: ReportOtherCorrs,
                 report_receipt_delivery_num: int, report_receipt_delivery_amnt: str, report_training_num: int,
                 report_training_amnt: str, report_credit_sales: ReportCreditSales,
                 report_credit_memos: ReportCreditMemos, report_pay_ins: ReportPayIns, report_pay_outs: ReportPayOuts,
                 report_grand_total_sales: str, report_grand_total_return: str,
                 report_grand_total_sales_net: str) -> None:
        self.report_id = report_id
        self.report_type = report_type
        self.company_ident = company_ident
        self.company_name = company_name
        self.report_date = report_date
        self.report_time = report_time
        self.register_id = register_id
        self.report_total_cash_sales = report_total_cash_sales
        self.report_art_groups = report_art_groups
        self.report_emp_art_groups = report_emp_art_groups
        self.report_payments = report_payments
        self.report_emp_payments = report_emp_payments
        self.report_cash_sales_vat = report_cash_sales_vat
        self.report_opening_change_float = report_opening_change_float
        self.report_emp_opening_change_floats = report_emp_opening_change_floats
        self.report_receipt_num = report_receipt_num
        self.report_open_cash_box_num = report_open_cash_box_num
        self.report_receipt_copy_num = report_receipt_copy_num
        self.report_receipt_copy_amnt = report_receipt_copy_amnt
        self.report_receipt_proforma_num = report_receipt_proforma_num
        self.report_receipt_proforma_amnt = report_receipt_proforma_amnt
        self.report_return_num = report_return_num
        self.report_return_amnt = report_return_amnt
        self.report_discount_num = report_discount_num
        self.report_discount_amnt = report_discount_amnt
        self.report_void_trans_num = report_void_trans_num
        self.report_void_trans_amnt = report_void_trans_amnt
        self.report_corr_lines = report_corr_lines
        self.report_price_inquiries = report_price_inquiries
        self.report_other_corrs = report_other_corrs
        self.report_receipt_delivery_num = report_receipt_delivery_num
        self.report_receipt_delivery_amnt = report_receipt_delivery_amnt
        self.report_training_num = report_training_num
        self.report_training_amnt = report_training_amnt
        self.report_credit_sales = report_credit_sales
        self.report_credit_memos = report_credit_memos
        self.report_pay_ins = report_pay_ins
        self.report_pay_outs = report_pay_outs
        self.report_grand_total_sales = report_grand_total_sales
        self.report_grand_total_return = report_grand_total_return
        self.report_grand_total_sales_net = report_grand_total_sales_net


class Event:
    event_id: int
    event_type: str
    event_date: str
    event_time: str
    emp_id: Optional[int]
    trans_id: Optional[int]
    event_text: Optional[str]
    event_report: Optional[EventReport]

    def __init__(self, event_id: int, event_type: str, event_date: str, event_time: str,
                 emp_id: Optional[int], trans_id: Optional[int], event_text: Optional[str],
                 event_report: Optional[EventReport]) -> None:
        self.event_id = event_id
        self.event_type = event_type
        self.event_date = event_date
        self.event_time = event_time
        self.emp_id = emp_id
        self.trans_id = trans_id
        self.event_text = event_text
        self.event_report = event_report


class Cashregister:
    """
    Phần tử máy tính tiền chứa tất cả dữ liệu của một điểm bán hàng (máy tính tiền).
    """
    register_id: str
    """
    Số ID của máy tính tiền (giống như
    số phải được in trên biên lai).
    Đây phải là một mô tả độc đáo về quan điểm của
    doanh thu. Không có quy định cụ thể về cách
    đại diện cho điều này. Tối thiểu nó phải là duy nhất trên
    từng địa điểm, và tốt nhất là trong một công ty.
    Ví dụ là sự kết hợp giữa ID giấy phép và
    phiên bản phần mềm. Tiêu chuẩn ngành khác duy nhất
    hệ thống đánh số có thể được sử dụng. Khi
    nhận dạng phần cứng thích hợp, duy nhất (nối tiếp
    nr) có thể được sử dụng.
    """
    reg_desc: str
    """
    Mô tả logic của máy tính tiền hoặc điểm của doanh thu.
    """
    # event: List[Event] -  có thể bỏ qua field này
    cashtransaction: List[Cashtransaction]



class Address(BaseModel):
    streetname: str
    number: int
    city: str
    postal_code: str
    region: str
    country: str

    def __init__(self, streetname: str, number: int, city: str, postal_code: str, region: str, country: str) -> None:
        self.streetname = streetname
        self.number = number
        self.city = city
        self.postal_code = postal_code
        self.region = region
        self.country = country

    # @field_validator('country')
    # def validate_country(self, country):
    #     pattern = r"^[A-Z]{2}$"
    #     if re.match(pattern, country):
    #         print("Valid country code")
    #     else:
    #         ValueError("Invalid country code")
    #
    # @field_validator('postal_code')
    # def validate_postal_code(self, postal_code):
    #     pattern = r"^\d{5}$"
    #     if re.match(pattern, postal_code):
    #         print("Valid postal code")
    #     else:
    #         ValueError("Invalid postal code")


class Location:
    name: str
    street_address: Address
    cashregister: Cashregister

    def __init__(self, name: str, street_address: Address, cashregister: Cashregister) -> None:
        self.name = name
        self.street_address = street_address
        self.cashregister = cashregister


class Period:
    period_number: int
    period_desc: str
    start_date_period: str
    start_time_period: str
    end_date_period: str
    end_time_period: str

    def __init__(self, period_number: int, period_desc: str, start_date_period: str, start_time_period: str,
                 end_date_period: str, end_time_period: str) -> None:
        self.period_number = period_number
        self.period_desc = period_desc
        self.start_date_period = start_date_period
        self.start_time_period = start_time_period
        self.end_date_period = end_date_period
        self.end_time_period = end_time_period


class Periods:
    period: Period

    def __init__(self, period: Period) -> None:
        self.period = period


class VatCodeDetail:
    vat_code: int
    """
    Mã số VAT được sử dụng bởi hệ thống máy tính tiền.
    """
    date_of_entry: str
    """
    Ngày mã số thuế GTGT được tạo trong
    hệ thống lần đầu tiên.
    """
    vat_desc: str
    """
    Mô tả mã VAT được sử dụng bởi máy tính tiền
    hệ thống.
    """
    standard_vat_code: int
    """
    Mã số thuế GTGT tương ứng theo quy định
    tài liệu “VAT/Thuế tiêu chuẩn SAF-T của Na Uy
    mã” trên tài liệu máy tính tiền SAF-T
    trang.
    """

    def __init__(self, vat_code: int, date_of_entry: str, vat_desc: str, standard_vat_code: int) -> None:
        self.vat_code = vat_code
        self.date_of_entry = date_of_entry
        self.vat_desc = vat_desc
        self.standard_vat_code = standard_vat_code


class VatCodeDetails:
    """
    Phần tử vat trong cashtransaction và/hoặc ctLine có thể được sử dụng để thể hiện vatCode với các giá trị. dateOfEntry được sử dụng để theo dõi
    từ thời điểm nào các mã đầu tiên có mặt trong hệ thống.
    Danh sách mã VAT tiêu chuẩn có hiệu lực bất kể các thay đổi về tỷ lệ phần trăm VAT, vì danh sách mã sẽ bị thay đổi nếu các loại được thêm/xóa không
    tỷ lệ thay đổi trong một mã. Thay đổi trong tương lai của danh sách mã VAT tiêu chuẩn sẽ bao gồm việc lập phiên bản với các khoảng thời gian hợp lệ.
    Tuy nhiên, nếu một số mã cụ thể của hệ thống (Mã vatCode) hợp lệ với cùng một mã tiêu chuẩn (mã VatCode tiêu chuẩn), thì chúng phải được liệt kê từng cái một.
    """
    vat_code_detail: List[VatCodeDetail]

    def __init__(self, vat_code_detail: List[VatCodeDetail]) -> None:
        self.vat_code_detail = vat_code_detail


class Company:
    """
    Chứa dữ liệu của công ty cơ thể đã cung cấp dữ liệu trong tệp kiểm toán
    """
    company_ident: int
    """
    Số tổ chức từ The Brønnøysund
    Trung tâm Đăng ký (Brønnøysundregistrene) hoặc trung tâm khác
    cơ quan nhà nước có liên quan. Trong trường hợp doanh nghiệp một người không có mã số tổ chức,
    số an sinh xã hội có thể được sử dụng.
    """
    company_name: str
    tax_registration_country: str
    """
    Mã quốc gia gồm hai chữ cái theo ISO 3166-1 alpha2 tiêu chuẩn.
    """
    tax_reg_ident: str
    """
    Mã số thuế GTGT (MVA) của công ty.
    Đây là số duy nhất/số tổ chức
    từ Trung tâm đăng ký Brønnøysund
    (Brønnøysundregistrene). yếu tố này là
    bắt buộc nếu công ty
    chịu thuế GTGT (MVA)
    """
    street_address: Address
    postal_address: Address
    vat_code_details: VatCodeDetails
    # optional Periods
    # periods: Periods
    # optional Employees
    # employees: Employees
    # optional Articles
    # articles: Articles
    # basics: Basics
    # """
    # Phần tử cơ bản được sử dụng để xác định các dữ liệu chủ khác nhau và dịch các mã cụ thể của hệ thống thành các mã tiêu chuẩn được xác định trước. Dữ liệu chủ
    # liên quan đến Máy tính tiền SAF-T của Na Uy chủ yếu là mã nhóm bài viết, mã giao dịch, mã cho phương thức thanh toán và
    # mã sự kiện.
    # Khi ghi lại các giao dịch và sự kiện khác nhau trong máy tính tiền, các mã cụ thể của hệ thống được ghi vào SAF-T Cash của Na Uy
    # Đăng ký tệp dữ liệu.
    # Cần có một yếu tố cơ bản tương ứng cho mỗi mã (hệ thống cụ thể) được bao gồm trong tệp dữ liệu Máy tính tiền SAF-T của Na Uy.
    # """
    location: Location
    """
    Chứa dữ liệu về vị trí thực tế của tiền mặt
    đăng ký, ví dụ như địa chỉ của một số
    thành lập.
    """


class Header(BaseModel):
    """
    Overall information about this Standard Audit file, cái này ở bên sở thuế sẽ cung cấp
    """
    fiscal_year: int
    """
    năm kiểm toán
    """
    start_date: str
    """
    Ngày đầu tiên của giai đoạn lựa chọn hồ sơ kiểm toán.
    """
    end_date: str
    """
    Ngày cuối cùng của giai đoạn lựa chọn hồ sơ kiểm toán.
    """
    cur_code: str
    """
    Dạng tiền tệ, ví dụ NOK
    """
    date_created: str
    """
    Ngày tệp kiểm toán được tạo.
    """
    time_created: str
    """
    Tg tệp kiểm toán được tạo.
    """
    software_desc: str
    """
    Mô tả phần mềm tạo ra cuộc kiểm toán
    tài liệu.
    """
    software_version: str
    """
    Version of the software that generated the audit
    file.
    """
    software_company_name: str
    auditfile_version: str
    header_comment: str
    user_id: int
    """
    ID của người dùng đã tạo tệp kiểm toán.
    """

    # @field_validator('fiscal_year')
    # def validate_fiscal_year(cls, v):
    #     pattern = r"^(19|20)\d{2}(-\d{2})?$"
    #     if re.match(pattern, v):
    #         return v
    #     else:
    #         raise ValueError('Invalid fiscal year')
    #
    # @field_validator('start_date')
    # def validate_start_date(cls, v):
    #     if not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
    #         raise ValueError('Invalid first day of selection period')
    #     return v
    #
    # @field_validator('end_date')
    # def validate_start_date(cls, v):
    #     if not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
    #         raise ValueError('Invalid first day of selection period')
    #     return v
    #
    # @field_validator('cur_code')
    # def validate_currency_code(self, cur_code):
    #     pattern = r"^[A-Z]{3}$"
    #     if re.match(pattern, cur_code):
    #         print("Valid currency code")
    #     else:
    #         raise ValueError('Invalid cur code')
    #
    # @field_validator('date_created')
    # def validate_date_created(self, date_created):
    #     pattern = r"^\d{4}-\d{2}-\d{2}$"
    #     if re.match(pattern, date_created):
    #         print("Valid dateCreated")
    #     else:
    #         raise ValueError('Invalid cur code')
    #
    # @field_validator('time_created')
    # def validate_time_created(self, time_created):
    #     pattern = r"^(2[0-3]|[01][0-9]):[0-5][0-9]$"
    #     if re.match(pattern, time_created):
    #         print("Valid timeCreated")
    #     else:
    #         raise ValueError('Invalid time created')


ex_header = Header(fiscal_year=2020,
                   start_date="2020-01-01",
                   end_date="2020-01-31",
                   cur_code="NOK",
                   date_created="2021-03-30",
                   time_created="10:40:00",
                   software_desc="Kassasystemet",
                   software_version="3.14.1.3",
                   software_company_name="Kassasystemer AS",
                   auditfile_version="1.0",
                   header_comment="Selection criteria: Location A",
                   user_id=1000)

print(object_to_xml(ex_header))


class Auditfile:
    header: Header
    company: Company
    xmlns: str
    xmlns_xsi: str
    xsi_schema_location: str

    def __init__(self, header: Header, company: Company, xmlns: str, xmlns_xsi: str, xsi_schema_location: str) -> None:
        self.header = header
        self.company = company
        self.xmlns = xmlns
        self.xmlns_xsi = xmlns_xsi
        self.xsi_schema_location = xsi_schema_location


class NorwaySAF:
    auditfile: Auditfile

    def __init__(self, auditfile: Auditfile) -> None:
        self.auditfile = auditfile
