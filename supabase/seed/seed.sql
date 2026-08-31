-- seed.sql — dados de demonstração (fictícios, sem dados pessoais reais)

insert into plans (code, name, max_companies, price_cents) values
  ('starter', 'Starter', 10, 9900),
  ('profissional', 'Profissional', 50, 24900),
  ('escritorio', 'Escritório', 200, 59900),
  ('enterprise', 'Enterprise', null, null)
on conflict (code) do nothing;

insert into rules (codigo, nome, descricao, uf, tipo_processo, condicao, severidade, mensagem, acao_sugerida, fonte, versao, ativo)
values (
  'PE-QSA-001',
  'Novo sócio sem dados obrigatórios',
  'Verifica se um novo sócio incluído em alteração de QSA possui os dados mínimos exigidos.',
  'PE',
  'alteracao_qsa',
  '{"campo": "novo_socio", "obrigatorios": ["nome", "cpf_cnpj", "qualificacao", "percentual_capital"]}'::jsonb,
  'erro',
  'Novo sócio informado sem todos os dados obrigatórios.',
  'Preencha nome, CPF/CNPJ, qualificação e percentual de capital do novo sócio antes de prosseguir.',
  'Regra interna — não configurada como exigência oficial confirmada.',
  1,
  true
)
on conflict (codigo) do nothing;
