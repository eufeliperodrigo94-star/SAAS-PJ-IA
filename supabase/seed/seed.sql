-- seed.sql — dados de demonstração (fictícios, sem dados pessoais reais)

insert into plans (code, name, max_companies, price_cents) values
  ('starter', 'Starter', 10, 9900),
  ('profissional', 'Profissional', 50, 24900),
  ('escritorio', 'Escritório', 200, 59900),
  ('enterprise', 'Enterprise', null, null)
on conflict (code) do nothing;

-- Regras determinísticas iniciais para PE (Dia 4). O "check" em `condicao` é
-- despachado por app/rules/checks.py — ver docs/RULES.md.

insert into rules (codigo, nome, descricao, uf, tipo_processo, condicao, severidade, mensagem, acao_sugerida, fonte, versao, ativo)
values
(
  'PE-CNAE-001',
  'Empresa sem CNAE cadastrado',
  'Toda empresa precisa de ao menos um CNAE antes de qualquer processo.',
  'PE',
  null,
  '{"check": "company_has_activity"}'::jsonb,
  'erro',
  'A empresa não possui nenhum CNAE cadastrado.',
  'Cadastre pelo menos um CNAE (principal) antes de prosseguir com o processo.',
  'Regra interna — não configurada como exigência oficial confirmada.',
  1,
  true
),
(
  'PE-END-001',
  'Empresa sem endereço cadastrado',
  'Toda empresa precisa de ao menos um endereço antes de qualquer processo.',
  'PE',
  null,
  '{"check": "company_has_address"}'::jsonb,
  'erro',
  'A empresa não possui nenhum endereço cadastrado.',
  'Cadastre o endereço da sede antes de prosseguir com o processo.',
  'Regra interna — não configurada como exigência oficial confirmada.',
  1,
  true
),
(
  'PE-QSA-001',
  'Alteração de QSA sem sócios cadastrados',
  'Alerta quando não há nenhum sócio cadastrado para uma alteração de QSA.',
  'PE',
  'alteracao_qsa',
  '{"check": "company_has_partners"}'::jsonb,
  'atencao',
  'Nenhum sócio cadastrado para esta alteração de QSA.',
  'Cadastre os sócios atuais e os pretendidos antes de continuar.',
  'Regra interna — não configurada como exigência oficial confirmada.',
  1,
  true
),
(
  'PE-QSA-002',
  'Soma de percentuais de capital divergente',
  'A soma dos percentuais de capital dos sócios deve totalizar 100%.',
  'PE',
  'alteracao_qsa',
  '{"check": "partners_percentual_sum", "tolerance": 0.01}'::jsonb,
  'erro',
  'A soma dos percentuais de capital dos sócios não totaliza 100%.',
  'Ajuste os percentuais de capital dos sócios até somarem exatamente 100%.',
  'Regra interna — não configurada como exigência oficial confirmada.',
  1,
  true
)
on conflict (codigo) do nothing;

-- Regras sourced dos manuais oficiais "Passo a Passo" da JUCEPE e do Manual de
-- Registro de Sociedade Limitada do DREI (IN DREI nº 81/2020, Anexo IV) — ver
-- docs/RULES.md para a citação completa de cada fonte.

insert into rules (codigo, nome, descricao, uf, tipo_processo, condicao, severidade, mensagem, acao_sugerida, fonte, versao, ativo)
values
(
  'PE-CNAE-002',
  'Mais de um CNAE marcado como principal',
  'O Requerimento Eletrônico da JUCEPE só aceita uma atividade principal por empresa.',
  'PE',
  null,
  '{"check": "at_most_one_primary_cnae"}'::jsonb,
  'erro',
  'Mais de um CNAE está marcado como principal. Escolha apenas um.',
  'Marque apenas uma atividade como principal; as demais devem ser secundárias.',
  'JUCEPE — Passo a Passo "Constituição": "Pode-se escolher apenas uma atividade principal e várias atividades secundárias (sem limite)".',
  1,
  true
),
(
  'PE-END-002',
  'Endereço da sede incompleto',
  'O endereço da sede deve ter logradouro, número, bairro, município, UF e CEP preenchidos.',
  'PE',
  null,
  '{"check": "address_fields_complete", "tipo": "sede"}'::jsonb,
  'erro',
  'O endereço da sede está incompleto (faltam campos obrigatórios).',
  'Preencha logradouro, número, bairro, município, UF e CEP do endereço da sede.',
  'DREI — Manual de Registro de Sociedade Limitada (IN DREI nº 81/2020, Anexo IV): o ato de inscrição/alteração exige o endereço completo da sede.',
  1,
  true
),
(
  'PE-CAP-001',
  'Capital social abaixo do valor de referência',
  'Alerta (não bloqueia) quando o capital social declarado na abertura está abaixo do valor de referência de mercado.',
  'PE',
  'abertura',
  '{"check": "company_capital_minimum", "minimo": 1000}'::jsonb,
  'atencao',
  'Capital social abaixo de R$ 1.000,00, referência usual de mercado para compatibilidade com o objeto social.',
  'Avalie se o capital social é compatível com o objeto social da empresa (não há piso legal, mas órgãos de análise costumam questionar valores muito baixos).',
  'Não há piso legal de capital social para LTDA no Brasil; R$ 1.000,00 é a referência de mercado/Redesim usada como alerta preventivo, não como exigência de arquivamento.',
  1,
  true
),
(
  'PE-CAP-002',
  'Capital social abaixo do valor de referência (alteração)',
  'Mesmo alerta de PE-CAP-001, aplicado a processos de alteração de capital.',
  'PE',
  'alteracao_capital',
  '{"check": "company_capital_minimum", "minimo": 1000}'::jsonb,
  'atencao',
  'Capital social abaixo de R$ 1.000,00, referência usual de mercado para compatibilidade com o objeto social.',
  'Avalie se o novo capital social é compatível com o objeto social da empresa.',
  'Não há piso legal de capital social para LTDA no Brasil; R$ 1.000,00 é a referência de mercado/Redesim usada como alerta preventivo, não como exigência de arquivamento.',
  1,
  true
)
on conflict (codigo) do nothing;
