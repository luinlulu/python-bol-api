from decimal import Decimal
from datetime import datetime

from bol.plaza.api import PlazaAPI

from httmock import HTTMock, urlmatch


ORDERS_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<bns:Orders
    xmlns:bns="http://plazaapi.bol.com/services/xsd/plazaapiservice-1.0.xsd">
  <bns:Order>
    <bns:OrderId>123</bns:OrderId>
    <bns:DateTimeCustomer>2015-09-23T12:30:36</bns:DateTimeCustomer>
    <bns:DateTimeDropShipper>2015-09-23T12:30:36</bns:DateTimeDropShipper>
    <bns:CustomerDetails>
      <bns:ShipmentDetails>
        <bns:SalutationCode>01</bns:SalutationCode>
        <bns:Firstname>Jan</bns:Firstname>
        <bns:Surname>Janssen</bns:Surname>
        <bns:Streetname>Shipmentstraat</bns:Streetname>
        <bns:Housenumber>42</bns:Housenumber>
        <bns:HousenumberExtended>bis</bns:HousenumberExtended>
        <bns:AddressSupplement>3 hoog achter</bns:AddressSupplement>
        <bns:ZipCode>1000 AA</bns:ZipCode>
        <bns:City>Amsterdam</bns:City>
        <bns:CountryCode>NL</bns:CountryCode>
        <bns:Email>nospam4me@myaccount.com</bns:Email>
        <bns:DeliveryPhoneNumber>12345</bns:DeliveryPhoneNumber>
        <bns:Company>The Company</bns:Company>
      </bns:ShipmentDetails>
      <bns:BillingDetails>
        <bns:SalutationCode>02</bns:SalutationCode>
        <bns:Firstname>Jans</bns:Firstname>
        <bns:Surname>Janssen</bns:Surname>
        <bns:Streetname>Billingstraat</bns:Streetname>
        <bns:Housenumber>1</bns:Housenumber>
        <bns:HousenumberExtended>a</bns:HousenumberExtended>
        <bns:AddressSupplement>Onder de brievenbus</bns:AddressSupplement>
        <bns:ZipCode>5000 ZZ</bns:ZipCode>
        <bns:City>Amsterdam</bns:City>
        <bns:CountryCode>NL</bns:CountryCode>
        <bns:Email>dontemail@me.net</bns:Email>
        <bns:DeliveryPhoneNumber>67890</bns:DeliveryPhoneNumber>
        <bns:Company>Bol.com</bns:Company>
      </bns:BillingDetails>
    </bns:CustomerDetails>
    <bns:OrderItems>
      <bns:OrderItem>
        <bns:OrderItemId>123</bns:OrderItemId>
        <bns:EAN>9789062387410</bns:EAN>
        <bns:OfferReference>PARTNERREF001</bns:OfferReference>
        <bns:Title>Regelmaat en Inbakeren</bns:Title>
        <bns:Quantity>1</bns:Quantity>
        <bns:OfferPrice>123.45</bns:OfferPrice>
        <bns:PromisedDeliveryDate>Binnen 24 uur</bns:PromisedDeliveryDate>
        <bns:TransactionFee>19.12</bns:TransactionFee>
      </bns:OrderItem>
    </bns:OrderItems>
  </bns:Order>
</bns:Orders>"""


PAYMENTS_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<bns:Payments
    xmlns:bns="http://plazaapi.bol.com/services/xsd/plazaapiservice-1.0.xsd">
  <bns:Payment>
    <bns:CreditInvoiceNumber>123</bns:CreditInvoiceNumber>
    <bns:DateTimePayment>2015-09-23T21:35:43</bns:DateTimePayment>
    <bns:PaymentAmount>425.77</bns:PaymentAmount>
    <bns:PaymentShipments>
      <bns:PaymentShipment>
        <bns:ShipmentId>456</bns:ShipmentId>
        <bns:OrderId>123001</bns:OrderId>
        <bns:PaymentShipmentAmount>425.77</bns:PaymentShipmentAmount>
        <bns:PaymentStatus>FINAL</bns:PaymentStatus>
        <bns:ShipmentDate>2015-09-23T21:35:43</bns:ShipmentDate>
        <bns:PaymentShipmentItems>
          <bns:PaymentShipmentItem>
            <bns:OrderItemId>123001001</bns:OrderItemId>
            <bns:EAN>9789062387410</bns:EAN>
            <bns:OfferReference>PARTNERREF001</bns:OfferReference>
            <bns:Quantity>1</bns:Quantity>
            <bns:OfferPrice>425.77</bns:OfferPrice>
            <bns:ShippingContribution>1.95</bns:ShippingContribution>
            <bns:TransactionFee>10.00</bns:TransactionFee>
            <bns:TotalAmount>425.77</bns:TotalAmount>
            <bns:ShipmentStatus>NORMAL</bns:ShipmentStatus>
          </bns:PaymentShipmentItem>
        </bns:PaymentShipmentItems>
      </bns:PaymentShipment>
    </bns:PaymentShipments>
  </bns:Payment>
</bns:Payments>"""


PROCESS_RESPONSE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<bns:ProcessOrdersResult
    xmlns:bns="http://plazaapi.bol.com/services/xsd/plazaapiservice-1.0.xsd">
    <bns:ProcessOrderId>123</bns:ProcessOrderId>
</bns:ProcessOrdersResult>"""


@urlmatch(path=r'/services/rest/orders/v2/$')
def orders_stub(url, request):
    return ORDERS_RESPONSE


@urlmatch(path=r'/services/rest/payments/v2/201501$')
def payments_stub(url, request):
    return PAYMENTS_RESPONSE


def test_orders():
    with HTTMock(orders_stub):
        api = PlazaAPI('api_key', 'api_secret', test=True)
        orders = api.orders.open()
        assert len(orders) == 1

        order = orders[0]
        assert order.OrderId == '123'

        assert order.CustomerDetails.BillingDetails.SalutationCode == '02'
        assert order.CustomerDetails.BillingDetails.Firstname == 'Jans'
        assert order.CustomerDetails.BillingDetails.Surname == 'Janssen'
        assert (
            order.CustomerDetails.BillingDetails.Streetname ==
            'Billingstraat')
        assert order.CustomerDetails.BillingDetails.Housenumber == '1'
        assert order.CustomerDetails.BillingDetails.HousenumberExtended == 'a'
        assert (
            order.CustomerDetails.BillingDetails.AddressSupplement ==
            'Onder de brievenbus')
        assert order.CustomerDetails.BillingDetails.ZipCode == '5000 ZZ'
        assert order.CustomerDetails.BillingDetails.City == 'Amsterdam'
        assert order.CustomerDetails.BillingDetails.CountryCode == 'NL'
        assert order.CustomerDetails.BillingDetails.Email == 'dontemail@me.net'
        assert (
            order.CustomerDetails.BillingDetails.DeliveryPhoneNumber ==
            '67890')
        assert order.CustomerDetails.BillingDetails.Company == 'Bol.com'

        assert order.CustomerDetails.ShipmentDetails.SalutationCode == '01'
        assert order.CustomerDetails.ShipmentDetails.Firstname == 'Jan'
        assert order.CustomerDetails.ShipmentDetails.Surname == 'Janssen'
        assert (
            order.CustomerDetails.ShipmentDetails.Streetname ==
            'Shipmentstraat')
        assert order.CustomerDetails.ShipmentDetails.Housenumber == '42'
        assert (
            order.CustomerDetails.ShipmentDetails.HousenumberExtended == 'bis')

        assert (
            order.CustomerDetails.ShipmentDetails.AddressSupplement ==
            '3 hoog achter')
        assert order.CustomerDetails.ShipmentDetails.ZipCode == '1000 AA'
        assert order.CustomerDetails.ShipmentDetails.City == 'Amsterdam'
        assert order.CustomerDetails.ShipmentDetails.CountryCode == 'NL'
        assert (
            order.CustomerDetails.ShipmentDetails.Email ==
            'nospam4me@myaccount.com')
        assert (
            order.CustomerDetails.ShipmentDetails.DeliveryPhoneNumber ==
            '12345')
        assert order.CustomerDetails.ShipmentDetails.Company == 'The Company'

        assert len(order.OrderItems) == 1
        item = order.OrderItems[0]

        assert item.OrderItemId == '123'
        assert item.EAN == '9789062387410'
        assert item.OfferReference == 'PARTNERREF001'
        assert item.Title == 'Regelmaat en Inbakeren'
        assert item.Quantity == 1
        assert item.OfferPrice == Decimal('123.45')
        assert item.PromisedDeliveryDate == 'Binnen 24 uur'
        assert item.TransactionFee == Decimal('19.12')


def test_order_process():
    @urlmatch(path=r'/services/rest/orders/v2/process$')
    def process_stub(url, request):
        assert request.body == """<?xml version="1.0" encoding="UTF-8"?>
<ProcessOrders
    xmlns="http://plazaapi.bol.com/services/xsd/plazaapiservice-1.0.xsd"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://plazaapi.bol.com/services/xsd/plazaapiservice-1.0.xsd">
    <Shipments>
        <Shipment>
            <OrderId>123</OrderId>
            <DateTime>2015-01-02T12:11:00</DateTime>
            <Transporter>
                <Code>DHLFORYOU</Code>
                <TrackAndTraceCode>1234</TrackAndTraceCode>
            </Transporter>
            <OrderItems>
                <Id>34567</Id>
            </OrderItems>
        </Shipment>
    </Shipments>
</ProcessOrders>
"""
        return PROCESS_RESPONSE

    with HTTMock(process_stub):
        api = PlazaAPI('api_key', 'api_secret', test=True)
        process_id = api.orders.process(
            order_id='123',
            date_time=datetime(2015, 1, 2, 12, 11, 0),
            code='1234',
            transporter_code='DHLFORYOU',
            order_item_ids=['34567'])
        assert process_id == '123'


def test_payments():
    with HTTMock(payments_stub):
        api = PlazaAPI('api_key', 'api_secret', test=True)
        payments = api.payments.payments(2015, 1)

        assert len(payments) == 1
        payment = payments[0]
        assert payment.PaymentAmount == Decimal('425.77')
        assert payment.DateTimePayment == datetime(2015, 9, 23, 21, 35, 43)
        assert payment.CreditInvoiceNumber == '123'
        assert len(payment.PaymentShipments) == 1
        shipment = payment.PaymentShipments[0]
        assert shipment.OrderId == '123001'
        assert shipment.ShipmentId == '456'
        assert shipment.PaymentShipmentAmount == Decimal('425.77')
        assert shipment.PaymentStatus == 'FINAL'
