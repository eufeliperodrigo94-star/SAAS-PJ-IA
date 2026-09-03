# RULES.md

Motor de regras determinístico (implementado no Dia 4: `app/rules/`). Regras são **dados
versionados** na tabela `rules`, não lógica espalhada pelo código.

## Campos de uma regra

`id, codigo, nome, descricao, uf, municipio, tipo_processo, condicao, severidade, mensagem,
acao_sugerida, fonte, versao, vigencia, ativo`.

`condicao` é um `jsonb` no formato `{"check": "<nome>", ...parâmetros}`. O motor
(`app/rules/engine.py`) despacha `check` para a função correspondente em
`app/rules/checks.py`. Uma regra com `uf`/`tipo_processo` nulos se aplica a qualquer
UF/processo; `municipio` e `vigencia_inicio`/`vigencia_fim` restringem ainda mais quando
preenchidos.

## Checks implementados (Dia 4)

| Check | O que verifica |
|---|---|
| `company_has_activity` | Empresa tem pelo menos um CNAE cadastrado. |
| `company_has_address` | Empresa tem pelo menos um endereço cadastrado. |
| `company_has_partners` | Empresa tem pelo menos um sócio cadastrado. |
| `partners_percentual_sum` | Soma dos `percentual_capital` dos sócios fecha em 100% (± `tolerance`). |
| `required_company_fields` | Campos informados em `fields` estão preenchidos na empresa. |

Novos checks entram como novas funções em `checks.py` + entrada no dicionário `CHECKS` —
nunca como `if`s soltos no motor.

## Severidade / resultado

- `ok`
- `atencao`
- `erro`

Cada resultado (`validations`) indica a regra aplicada (`rule_id`), a evidência (`evidence`,
o que o check mediu) e a ação sugerida — nunca apenas um booleano. Quando uma regra referencia
um `check` inexistente, o motor não inventa um resultado: marca como "não configurada"
(severidade `atencao`) em vez de afirmar algo indevido.

## Execução e status do processo

`POST /processes/{id}/validate` roda todas as regras ativas aplicáveis, substitui as
`validations` anteriores do processo e recalcula seu `status`:

- Algum resultado `erro` → `pendente_correcao`.
- Sem erro mas com pelo menos um resultado → `pronto_para_protocolo`.
- Nenhuma regra aplicável → mantém `em_validacao`.

## Regra de ouro

Se uma regra pode ser executada deterministicamente, **não chamar LLM**. Quando uma regra ainda
não estiver cadastrada/configurada para uma UF/processo, marcar como "não configurada" — nunca
inventar um requisito legal.
