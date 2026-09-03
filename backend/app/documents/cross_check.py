"""Cruzamento de dados: cadastro informado × documento enviado (ver docs/PROJECT.md).

Puramente determinístico — não chama IA. A extração dos dados do documento
(texto → JSON) é feita à parte pelo AI Router; este módulo só compara o que
já está estruturado.
"""


def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def _normalize_cnpj(value: str | None) -> str:
    return "".join(ch for ch in (value or "") if ch.isdigit())


def compare_company_data(company: dict, partners: list[dict], extracted: dict) -> list[dict]:
    results = []

    extracted_razao = extracted.get("razao_social")
    if extracted_razao and company.get("razao_social"):
        results.append(
            {
                "campo": "razao_social",
                "cadastro": company["razao_social"],
                "documento": extracted_razao,
                "divergente": _normalize(extracted_razao) != _normalize(company["razao_social"]),
            }
        )

    extracted_cnpj = extracted.get("cnpj")
    if extracted_cnpj and company.get("cnpj"):
        results.append(
            {
                "campo": "cnpj",
                "cadastro": company["cnpj"],
                "documento": extracted_cnpj,
                "divergente": _normalize_cnpj(extracted_cnpj) != _normalize_cnpj(company["cnpj"]),
            }
        )

    cadastro_names = {_normalize(p.get("nome")) for p in partners if p.get("nome")}
    for socio in extracted.get("socios") or []:
        nome = (socio or {}).get("nome")
        if not nome:
            continue
        found = _normalize(nome) in cadastro_names
        results.append(
            {
                "campo": f"socio:{nome}",
                "cadastro": "presente" if found else "ausente",
                "documento": nome,
                "divergente": not found,
            }
        )

    return results
