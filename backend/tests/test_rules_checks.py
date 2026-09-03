from app.rules.checks import (
    company_has_activity,
    company_has_address,
    company_has_partners,
    partners_percentual_sum,
    required_company_fields,
)


def test_company_has_activity():
    passed, evidence = company_has_activity({"activities": []}, {})
    assert not passed
    assert evidence == {"total_cnaes": 0}

    passed, _ = company_has_activity({"activities": [{"cnae_code": "0000-0/00"}]}, {})
    assert passed


def test_company_has_address():
    passed, _ = company_has_address({"addresses": []}, {})
    assert not passed

    passed, _ = company_has_address({"addresses": [{"id": "a1"}]}, {})
    assert passed


def test_company_has_partners():
    passed, _ = company_has_partners({"partners": []}, {})
    assert not passed


def test_partners_percentual_sum_ok():
    context = {"partners": [{"percentual_capital": 60}, {"percentual_capital": 40}]}
    passed, evidence = partners_percentual_sum(context, {})
    assert passed
    assert evidence["soma_percentual_capital"] == 100


def test_partners_percentual_sum_mismatch():
    context = {"partners": [{"percentual_capital": 60}, {"percentual_capital": 30}]}
    passed, evidence = partners_percentual_sum(context, {})
    assert not passed
    assert evidence["soma_percentual_capital"] == 90


def test_required_company_fields():
    context = {"company": {"cnpj": None, "razao_social": "Acme"}}
    passed, evidence = required_company_fields(context, {"fields": ["cnpj", "razao_social"]})
    assert not passed
    assert evidence["campos_ausentes"] == ["cnpj"]
