# RULES.md

Motor de regras determinístico (implementação a partir do Dia 4). Regras são **dados
versionados**, não lógica espalhada pelo código.

## Campos de uma regra

`id, codigo, nome, descricao, uf, municipio, tipo_processo, condicao, severidade, mensagem,
acao_sugerida, fonte, versao, vigencia, ativo`.

## Severidade / resultado

- `OK`
- `ATENCAO`
- `ERRO`

Cada resultado deve indicar a regra aplicada, a evidência e a ação sugerida — nunca apenas um
booleano.

## Regra de ouro

Se uma regra pode ser executada deterministicamente, **não chamar LLM**. Quando uma regra ainda
não estiver cadastrada/configurada para uma UF/processo, marcar como "não configurada" — nunca
inventar um requisito legal.
