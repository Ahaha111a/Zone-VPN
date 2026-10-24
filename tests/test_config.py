from config import PLANS
def test_owner_prices_unchanged():
 assert [PLANS[x].price_rub for x in ("m1","m2","m3")]==[499,1999,2999]
def test_only_three_requested_terms():
 assert set(PLANS)=={"m1","m2","m3"}

def test_sales_and_vpn_are_fail_closed_by_default():
    from config import settings
    assert settings.sales_enabled is False
    assert settings.payment_delivery_ready is False
    assert settings.vpn_mode == "disabled"
