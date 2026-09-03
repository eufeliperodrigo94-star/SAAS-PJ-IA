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

## Checks sourced de manuais oficiais da JUCEPE/DREI (pós-MVP)

| Check | O que verifica | Fonte |
|---|---|---|
| `at_most_one_primary_cnae` | No máximo um CNAE marcado como principal. | JUCEPE — Passo a Passo "Constituição": "Pode-se escolher apenas uma atividade principal e várias atividades secundárias (sem limite)". |
| `address_fields_complete` | Endereço do `tipo` informado (padrão `sede`) tem logradouro, número, bairro, município, UF e CEP preenchidos. | DREI — Manual de Registro de Sociedade Limitada (IN DREI nº 81/2020, Anexo IV): exige endereço completo no ato de inscrição/alteração. |
| `company_capital_minimum` | Capital social ≥ `minimo` (padrão R$ 1.000,00). **Sempre `atencao`, nunca `erro`** — não há piso legal de capital para LTDA no Brasil; é só a referência de mercado/Redesim. | Prática de mercado/Redesim; não é exigência de arquivamento na Junta. |

Regras seed (`supabase/seed/seed.sql`): `PE-CNAE-002`, `PE-END-002`, `PE-CAP-001` (abertura),
`PE-CAP-002` (alteração de capital) — cada uma com a fonte completa no campo `fonte`.

Novos checks entram como novas funções em `checks.py` + entrada no dicionário `CHECKS` —
nunca como `if`s soltos no motor. Nunca afirmar que algo é "exigência legal" sem citar a fonte
oficial no campo `fonte` da regra — se a fonte é incerta, a regra é apenas "interna" (como as do
Dia 4) e nunca deve usar severidade `erro` sem essa confirmação.

## Tipos de processo (`process_type`)

`abertura`, `alteracao_qsa`, `alteracao_endereco`, `alteracao_cnae`, `alteracao_capital`,
`alteracao_administrador`, `alteracao_nome_objeto`, `alteracao_porte` (enquadramento/
reenquadramento/desenquadramento ME-EPP), `transferencia_uf` (transferência de sede de PE para
outra UF) — os dois últimos adicionados na migration `0007_process_types_jucepe.sql`, a partir
dos manuais oficiais "Passo a Passo — Alteração de Porte" e "Passo a Passo — Transferência de PE
para Outra UF" da JUCEPE.

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

## Regra conhecida e ainda não implementada (falta dado, não falta regra)

O manual "Passo a Passo — Módulo MAT — Processo Expirado" da JUCEPE documenta que, após o
deferimento da constituição, o usuário tem **90 dias corridos** para preencher o Módulo de
Administração Tributária (MAT) na Receita Federal e obter o CNPJ; perdido o prazo, é preciso
refazer viabilidade e DBE do zero. Não implementamos essa regra ainda porque o schema atual não
guarda a data de deferimento do processo na Junta — adicionar isso exigiria uma coluna nova em
`processes` (ex.: `deferido_em`) antes de dar para calcular o prazo. Registrado aqui para não se
perder, não para inventar um campo às pressas.

## Regra de ouro

Se uma regra pode ser executada deterministicamente, **não chamar LLM**. Quando uma regra ainda
não estiver cadastrada/configurada para uma UF/processo, marcar como "não configurada" — nunca
inventar um requisito legal.
