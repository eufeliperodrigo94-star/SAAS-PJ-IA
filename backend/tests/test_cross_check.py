from app.documents.cross_check import compare_company_data


def test_matching_razao_social_and_cnpj_not_divergent():
    company = {"razao_social": "Acme LTDA", "cnpj": "12.345.678/0001-90"}
    extracted = {"razao_social": "acme ltda", "cnpj": "12345678000190"}

    results = compare_company_data(company, [], extracted)

    assert all(not r["divergente"] for r in results)


def test_divergent_razao_social():
    company = {"razao_social": "Acme LTDA", "cnpj": None}
    extracted = {"razao_social": "Beta LTDA"}

    results = compare_company_data(company, [], extracted)

    assert results[0]["divergente"]


def test_partner_not_in_registration_is_divergent():
    company = {"razao_social": None, "cnpj": None}
    partners = [{"nome": "Maria Silva"}]
    extracted = {"socios": [{"nome": "João Souza"}]}

    results = compare_company_data(company, partners, extracted)

    assert results[0]["campo"] == "socio:João Souza"
    assert results[0]["divergente"]


def test_partner_present_in_registration_is_not_divergent():
    company = {"razao_social": None, "cnpj": None}
    partners = [{"nome": "Maria Silva"}]
    extracted = {"socios": [{"nome": "maria silva"}]}

    results = compare_company_data(company, partners, extracted)

    assert not results[0]["divergente"]


def test_fields_absent_from_extraction_are_skipped():
    company = {"razao_social": "Acme LTDA", "cnpj": "123"}
    results = compare_company_data(company, [], {})

    assert results == []
