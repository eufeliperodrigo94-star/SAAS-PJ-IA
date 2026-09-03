-- 0007_process_types_jucepe.sql
-- Dois tipos de processo reais da JUCEPE, vistos nos manuais oficiais
-- "Passo a Passo — Alteração de Porte" e "Passo a Passo — Transferência de
-- PE para Outra UF", que ainda não existiam no enum inicial.

alter type process_type add value if not exists 'alteracao_porte';
alter type process_type add value if not exists 'transferencia_uf';
