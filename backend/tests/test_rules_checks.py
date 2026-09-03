from app.rules.checks import (
    address_fields_complete,
    at_most_one_primary_cnae,
    company_capital_minimum,
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


def test_at_most_one_primary_cnae_passes_with_zero_or_one():
    passed, evidence = at_most_one_primary_cnae({"activities": []}, {})
    assert passed
    assert evidence["total_cnaes_principais"] == 0

    context = {"activities": [{"is_primary": True}, {"is_primary": False}]}
    passed, evidence = at_most_one_primary_cnae(context, {})
    assert passed
    assert evidence["total_cnaes_principais"] == 1


def test_at_most_one_primary_cnae_fails_with_two():
    context = {"activities": [{"is_primary": True}, {"is_primary": True}]}
    passed, evidence = at_most_one_primary_cnae(context, {})
    assert not passed
    assert evidence["total_cnaes_principais"] == 2


def _address(**overrides) -> dict:
    base = {
        "tipo": "sede",
        "logradouro": "Av. Conselheiro Aguiar",
        "numero": "1200",
        "bairro": "Boa Viagem",
        "municipio": "Recife",
        "uf": "PE",
        "cep": "51020-020",
    }
    return {**base, **overrides}


def test_address_fields_complete_passes_when_all_present():
    context = {"addresses": [_address()]}
    passed, evidence = address_fields_complete(context, {})
    assert passed
    assert evidence["campos_ausentes"] == []


def test_address_fields_complete_fails_when_missing_fields():
    context = {"addresses": [_address(cep=None, numero="")]}
    passed, evidence = address_fields_complete(context, {})
    assert not passed
    assert set(evidence["campos_ausentes"]) == {"cep", "numero"}


def test_address_fields_complete_fails_when_no_address_of_type():
    context = {"addresses": [_address(tipo="filial")]}
    passed, evidence = address_fields_complete(context, {"tipo": "sede"})
    assert not passed
    assert evidence["motivo"] == "endereço não cadastrado"


def test_company_capital_minimum_passes_above_threshold():
    context = {"company": {"capital_social": 1000}}
    passed, evidence = company_capital_minimum(context, {"minimo": 1000})
    assert passed
    assert evidence["capital_social"] == 1000


def test_company_capital_minimum_fails_below_or_missing():
    passed, evidence = company_capital_minimum({"company": {"capital_social": 500}}, {"minimo": 1000})
    assert not passed
    assert evidence["minimo_recomendado"] == 1000

    passed, _ = company_capital_minimum({"company": {"capital_social": None}}, {"minimo": 1000})
    assert not passed
